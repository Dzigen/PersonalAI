from dataclasses import dataclass
from dataclasses import dataclass, field
from typing import List, Dict, Set, Union, Tuple
import numpy as np
import math
from tqdm import tqdm
import torch
from time import time

from ...db_drivers.tree_driver.utils import TreeNodeType, TreeNode, TreeIdType
from .configs import DEFAULT_SUMMN_TASK_CONFIG, NODESTREE_MODEL_LOG_PATH, \
    SUMMNODES_VDB_DEFAULT_DRIVER_CONFIG, LEAFNODES_VDB_DEFAULT_DRIVER_CONFIG, \
        TREE_DB_DEFAULT_DRIVER_CONFIG
from ...utils import Logger, AgentTaskSolver, AgentTaskSolverConfig, ReturnStatus
from ...utils.data_structs import Triplet, NodeType, create_id
from ...utils.errors import ReturnStatus
from ...agents import AgentDriver, AgentDriverConfig
from ...db_drivers.kv_driver import KeyValueDriverConfig
from ...db_drivers.vector_driver import VectorDriver, VectorDriverConfig, VectorDBInstance
from ...db_drivers.tree_driver import TreeDriver, TreeDriverConfig
from ...db_drivers.vector_driver.embedders import EmbedderModel, EmbedderModelConfig

@dataclass
class NodesTreeModelConfig:
    vectordb_leafnodes_config: VectorDriverConfig = field(default_factory=lambda: LEAFNODES_VDB_DEFAULT_DRIVER_CONFIG)
    vectordb_summnodes_config: VectorDriverConfig = field(default_factory=lambda: SUMMNODES_VDB_DEFAULT_DRIVER_CONFIG)
    embedder_config: EmbedderModelConfig = field(default_factory=lambda: EmbedderModelConfig())

    treedb_config: TreeDriverConfig = field(default_factory=lambda: TREE_DB_DEFAULT_DRIVER_CONFIG)

    adriver_config: AgentDriverConfig = field(default_factory=lambda: AgentDriverConfig())
    nodes_summarization_task_config: AgentTaskSolverConfig = field(default_factory=lambda: DEFAULT_SUMMN_TASK_CONFIG)

    e2n_sim_threshold: float = 0.4
    depth_rate: float = 0.5
    nodes_aggregation_mechanism: str = "sequencial" # "sequencial" | "parallel"

    log: Logger = field(default_factory=lambda: Logger(NODESTREE_MODEL_LOG_PATH))
    verbose: bool = False

class NodesTreeModel:
    def __init__(self, config: NodesTreeModelConfig = NodesTreeModelConfig(),
                 cache_kvdriver_config: KeyValueDriverConfig = None):
        self.config = config

        self.treedb_conn = TreeDriver.connect(self.config.treedb_config)
        self.vectordb_leafnodes_conn = VectorDriver.connect(config.vectordb_leafnodes_config)
        self.vectordb_summnodes_conn = VectorDriver.connect(config.vectordb_summnodes_config)
        self.embedder = EmbedderModel(config.embedder_config)

        self.agent = AgentDriver.connect(config.adriver_config)
        self.nodes_summarization_solver = AgentTaskSolver(
            self.agent, self.config.nodes_summarization_task_config, cache_kvdriver_config)

        self.log = self.config.log
        self.verbose = self.config.verbose

    def check_consistency(self):
        self.treedb_conn.check_consistency()

        leaf_vnodes_count = self.vectordb_leafnodes_conn.count_items()
        summ_vnodes_count = self.vectordb_summnodes_conn.count_items()
        tnodes_count = self.treedb_conn.count_items()

        # грубая проверка (нужно, чтобы каждому элементу из векторных бд
        # соответствовала вершина из графовой бд)
        assert leaf_vnodes_count == tnodes_count['leaf']
        assert summ_vnodes_count == tnodes_count['summarized']

    def get_tree_maxdepth(self):
        # TODO
        pass

    def expand_tree(self, triplets: List[Triplet], status_bar: bool = True) -> Dict[str, Set[str]]:

        # Отбираем уникальные object-вершины
        unique_object_nodes = dict()
        for triplet in triplets:
            cur_node = triplet.start_node
            if cur_node.type == NodeType.object:
                unique_object_nodes[cur_node.id] = cur_node

            cur_node = triplet.end_node
            if cur_node.type == NodeType.object:
                unique_object_nodes[cur_node.id] = cur_node
        object_nodes = unique_object_nodes.values()
        self.log(f"В {len(triplets)} триплетах (всего {len(triplets)*2} вершин) содержится {len(object_nodes)} \
                 уникальных (по строковому представлению) object-вершин.", verbose=self.verbose)

        # Добавляем вершины в дерево
        process = tqdm(object_nodes) if status_bar else object_nodes
        existed_node_ids, added_node_ids = [], []
        for node in process:
            status = self.add_node(node.id, node.name)

            if status == ReturnStatus.already_exist:
                existed_node_ids.append(node.id)
            else:
                added_node_ids.append(node.id)

        self.log(f"all/unique/existed/added nodes - {len(triplets)*2}/{len(object_nodes)}/{len(existed_node_ids)}/{len(added_node_ids)}", verbose=self.config.verbose)
        return {'existed_nodes': existed_node_ids, 'added_nodes': added_node_ids}

    def add_node(self, new_node_strid: str, new_node_text: str) -> ReturnStatus:
        status = ReturnStatus.success

        # проверка вершины, на существование в дереве
        if self.treedb_conn.item_exist(new_node_strid, type=TreeIdType.str):
            status = ReturnStatus.already_exist
            return status

        # Поиск parent-вершины, к которой будет добавлена новая child-вершина
        traversed_nodes_ids, parent_node = self.traverse_tree(new_node_text)
        # вызов llm для перегенерации text-полей у пройденных вершин
        new_text_summaries = self.summarize_path_nodes(traversed_nodes_ids, new_node_text)

        # обновление/добвавление summarize-вершин в соответствующую векторную бд
        self.update_vectordb_info(TreeNodeType.summarized, traversed_nodes_ids, new_text_summaries)
        # обновить информацию в summarize-вершинах в соответствующей графовой бд
        self.update_treedb_info(traversed_nodes_ids, new_text_summaries, new_node_strid, parent_node)

        # обновление/добвавление leaf-вершин в соответствующую векторную бд
        self.update_vectordb_info(TreeNodeType.leaf, [new_node_strid], [new_node_text])
        # прикрепить новую leaf-вершину к выбранной parent-вершине в дереве
        self.attach_node_to_tree(parent_node.id, new_node_text, {'str_id': new_node_strid, 'depth': len(traversed_nodes_ids)})

        return status

    def traverse_tree(self, newnode_text: str) -> Tuple[TreeNode, List[str]]:
        parent_node, traversed_nodes_ids = None, []
        newnode_embedding = self.embedder.encode_queries([newnode_text])[0]
        newnode_vinstance = VectorDBInstance(embedding=newnode_embedding)
        parent_node_id = self.treedb_conn.root_node_id
        cur_depth = 0

        stop_flag = False
        while not stop_flag:
            # Получаем child-вершины для текущей parent-вершины
            child_nodes = self.treedb_conn.get_child_nodes(parent_node_id)

            # Оцениваем семантическое расстояние [distance] между child-вершинами (с типом leaf)
            # у текущей parent-вершины и newnode_text
            leaf_nodes = list(filter(lambda node: node.type == TreeNodeType.leaf, child_nodes))
            strid2leafid_map = {node.prop['str_id']: node.id for node in leaf_nodes}
            leaf_nodes_strids = list(strid2leafid_map.keys())
            if len(leaf_nodes_strids) > 0:
                raw_scored_leafnodes = self.vectordb_leafnodes_conn.retrieve(
                    query_instances=[newnode_vinstance], n_results=len(leaf_nodes_strids),
                    subset_ids=leaf_nodes_strids, includes=[])[0]
                # переводим значения семантического расстояния [distance] в семантическую близость [similarity]
                scored_leafnodes = list(map(lambda pair: (1-pair[0], strid2leafid_map[pair[1].id]), raw_scored_leafnodes))
            else:
                scored_leafnodes = []

            # Оцениваем семантическое расстояние между child-вершинами (с типом summarized)
            # у текущей parent-вершины и newnode_text
            summ_nodes = list(filter(lambda node: node.type == TreeNodeType.summarized, child_nodes))
            summ_nodes_ids = list(map(lambda node: node.id, summ_nodes))
            if len(summ_nodes_ids) > 0:
                raw_scored_summnodes = self.vectordb_summnodes_conn.retrieve(
                    query_instances=[newnode_vinstance], n_results=len(summ_nodes_ids),
                    subset_ids=summ_nodes_ids, includes=[])[0]
                # переводим значения семантического расстояния [distance] в семантическую близость [similarity]
                scored_summnodes = list(map(lambda pair: (1-pair[0], pair[1].id), raw_scored_summnodes))
            else:
                scored_summnodes = []

            # Выполняем фильтрацию child-вершин на основании их семантической близости к newnode_text
            # по адаптивному пороговому значению
            cur_maxdepth = self.treedb_conn.get_tree_maxdepth()
            adaptive_coeff = 0 if cur_maxdepth < 1 else np.exp((self.config.depth_rate * cur_depth) / cur_maxdepth)
            adaptive_threshold = self.config.e2n_sim_threshold * adaptive_coeff
            filtered_child_nodes = list(filter(lambda scored_node: scored_node[0] >= adaptive_threshold, scored_leafnodes + scored_summnodes))

            # Если после фильтрации не осталось ни одной вершины, в которую можно выполнить переход,
            # то завершаем обход дерева, иначе выбираем самую семантически-близкую [similarity] вершину в качестве
            # следующей parent-вершины.
            if len(filtered_child_nodes) < 1:
                parent_node = self.treedb_conn.read([parent_node_id])[0]
                stop_flag = True
            else:
                sorted_child_nodes = sorted(filtered_child_nodes, key=lambda p: p[0], reverse=True)
                parent_node_id = sorted_child_nodes[0][1]
                traversed_nodes_ids.append(parent_node_id)
                cur_depth += 1

        return parent_node, traversed_nodes_ids

    def summarize_path_nodes(self, traversed_nodes_ids: List[str], newnode_text: str) -> List[str]:
        new_text_summaries = []
        for node_id in traversed_nodes_ids[::-1]:
            curparent_node = self.treedb_conn.read([node_id], ids_type=TreeIdType.external)[0]
            parent_text = curparent_node.text
            parent_descendants_num = curparent_node.props.get('descendants_num', 0)

            if self.config.nodes_aggregation_mechanism == 'sequencial':
                prev_summ_text = newnode_text if len(new_text_summaries) < 1 else new_text_summaries[-1]
                summ_text, solve_status = self.nodes_summarization_solver.solve(
                    current_content=parent_text, new_content=prev_summ_text,
                    n_descendants=parent_descendants_num)

            elif self.config.nodes_aggregation_mechanism == 'parallel':
                summ_text, solve_status = self.nodes_summarization_solver.solve(
                    current_content=parent_text, new_content=newnode_text,
                    n_descendants=parent_descendants_num)

            else:
                raise ValueError

            # Если в процессе парсинга ответа llm-агента возникла ошибка,
            # то выполняем наивную суммаризацию
            if solve_status != ReturnStatus.success:
                summ_text = f"{parent_text}, {newnode_text}"

            new_text_summaries.append(summ_text)

        return new_text_summaries[::-1]

    def update_vectordb_info(self, vecdb_type: TreeNodeType, ids: List[str], new_texts: List[str]) -> None:
        torch.cuda.empty_cache()
        embs = self.embedder.encode_passages(new_texts, batch_size=16)
        formated_instances = [VectorDBInstance(id=id, document=doc, embedding=emb, metadata={'id': id})
                            for id, doc, emb in zip(ids, new_texts, embs)]

        if vecdb_type == TreeNodeType.summarized:
            self.vectordb_summnodes_conn.upsert(formated_instances)
        elif vecdb_type == TreeNodeType.leaf:
            self.vectordb_leafnodes_conn.create(formated_instances)
        else:
            raise KeyError

    def update_treedb_info(self, ids: List[str], texts: List[str], new_node_strid: str, parent_node: TreeNode) -> None:
        if len(ids) > 1:
            # У всех summarized-вершин обновляем значения text- и других-полей
            for node_id, new_text in zip(ids[:-1],texts[:-1]):
                cur_node = self.treedb_conn.read([node_id], ids_type=TreeIdType.external)[0]
                cur_node.text = new_text
                cur_node.props['descendants_num'] += 1
                cur_node.props['aggregated_str_ids'].append(new_node_strid)
                self.treedb_conn.update([cur_node])

            # Eсли последняя вершина имеет тип leaf, то меняем её тип на summarized,
            # добавляем descendants_num-поле и удаляем str_id-поле
            if parent_node.type == TreeNodeType.leaf:
                self.change_node_to_summarized(parent_node, new_text=texts[-1])
                # перевешиваем leaf-вершину, на переформатированную/последнюю summarized-вершину
                self.attach_node_to_tree(ids[-1], parent_node.text, parent_node.props)

    def attach_node_to_tree(self, pn_id: str, ln_text: str, ln_props: Dict[str, object]) -> None:
        new_external_id = create_id(seed=str(time()))
        leaf_node = TreeNode(id=new_external_id, text=ln_text, type=TreeNodeType.leaf, props=ln_props)
        self.treedb_conn.create(pn_id, leaf_node)

    def change_node_to_summarized(self, old_node: TreeNode, new_text: str) -> None:
        # обновляем информацию в соответствующей графовой бд
        summarized_node = TreeNode(
            id=old_node.id, text=new_text, type=TreeNodeType.summarized,
            props=old_node.props)
        summarized_node.props['descendants_num'] = 0
        summarized_node.props['aggregated_str_ids'] = []
        del summarized_node.props['str_id']

        self.treedb_conn.update([summarized_node])

    def match_entitie2objects(self, entitie: str, strategy: str = 'collapsed', distance_threshold: float = 0.4, fetch_k: int = 1) -> List[VectorDBInstance]:

        if strategy == 'collapsed':
            entitie_embedding = self.embedder.encode_queries([entitie])[0]
            entitie_vinstance = VectorDBInstance(embedding=entitie_embedding)

            # извлекается самая релевантная к entitie вершина из leaf-бд
            raw_scored_leafnodes = self.vectordb_leafnodes_conn.retrieve(
                    query_instances=[entitie_vinstance], n_results=fetch_k,
                    includes=['documents'])[0]
            filtered_leafnodes = list(filter(lambda pair: pair[0] <= distance_threshold, raw_scored_leafnodes))
            best_leafnode = None
            if len(filtered_leafnodes) > 0:
                best_leafnode = sorted(filtered_leafnodes, key=lambda pair: pair[0], reverse=False)[0]

            # извлекается самая релевантная к entitie вершина из summarized-бд
            raw_scored_summnodes = self.vectordb_summnodes_conn.retrieve(
                    query_instances=[entitie_vinstance], n_results=fetch_k,
                    includes=['documents'])[0]
            filtered_summnodes = list(filter(lambda pair: pair[0] <= distance_threshold, raw_scored_summnodes))
            best_summnode = None
            if len(filtered_summnodes) > 0:
                best_summnode = sorted(filtered_summnodes, key=lambda pair: pair[0], reverse=False)[0]

            # из них выбирвается самая релевантная
            if best_summnode[0] < best_leafnode[0]:
                # в случае, если summarized-вершина семантически ближе к entitie,
                # то ей сопоставляются все её (summarized-вершины) вершиным-потомки
                summ_node = self.treedb_conn.read([best_summnode[1].id])[0]
                descendants_nodes_strids = summ_node.props['aggregated_str_ids']
                matched_nodes = self.vectordb_leafnodes_conn.read(descendants_nodes_strids)
            else:
                matched_nodes = self.vectordb_leafnodes_conn.read([best_leafnode.id])

        elif strategy == 'traversal':
            # TODO
            raise NotImplementedError
        else:
            raise ValueError

        return matched_nodes

    def reduce_tree(self, triplets: List[Triplet], delete_info: Dict[int, Dict[str, bool]]):
        # TODO
        pass

    def count_items(self):
        return {
            'tree': self.treedb_conn.count_items(),
            'vector_leafnodes': self.vectordb_leafnodes_conn.count_items(),
            'vector_summnodes': self.vectordb_summnodes_conn.count_items()}

    def clear(self):
        self.vectordb_leafnodes_conn.clear()
        self.vectordb_summnodes_conn.clear()
        self.treedb_conn.clear()
