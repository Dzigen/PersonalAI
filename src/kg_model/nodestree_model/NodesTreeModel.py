from dataclasses import dataclass
from dataclasses import dataclass, field
from typing import List, Dict, Set, Union, Tuple
import numpy as np
import math
from tqdm import tqdm
import torch

from .utils import TreeNodeType, TreeNode
from ...utils import Logger, AgentTaskSolver, AgentTaskSolverConfig, ReturnStatus
from ...utils.data_structs import Triplet, NodeType
from ...agents import AgentDriver, AgentDriverConfig
from ...db_drivers.kv_driver import KeyValueDriverConfig
from ...db_drivers.vector_driver import VectorDriver, VectorDriverConfig, VectorDBConnectionConfig, VectorDBInstance
from ...db_drivers.tree_driver import TreeDriver, TreeDriverConfig
from ...db_drivers.vector_driver.embedders import EmbedderModel, EmbedderModelConfig

NODESTREE_MODEL_LOG_PATH = 'log/kg_model/nodes_tree'

SUMMNODES_VDB_DEFAULT_DRIVER_CONFIG = VectorDriverConfig(
    db_vendor='chroma', db_config=VectorDBConnectionConfig(
        conn={'path':"../data/graph_structures/vectorized_triplets/default_densedb"},
        db_info={'db': 'default_db', 'table': "vectorized_summarizednodes"}))

BASE_VDB_DEFAULT_DRIVER_CONFIG = VectorDriverConfig(
    db_vendor='chroma', db_config=VectorDBConnectionConfig(
        conn={'path':"../data/graph_structures/vectorized_triplets/default_densedb"},
        db_info={'db': 'default_db', 'table': "vectorized_nodes"}))

TREE_DB_DEFAULT_DRIVER_CONFIG = TreeDriverConfig(db_vendor='neo4j', db_config=...)

@dataclass
class NodesTreeModelConfig:
    vectordb_leafnodes_config: VectorDriverConfig = field(default_factory=lambda: BASE_VDB_DEFAULT_DRIVER_CONFIG)
    vectordb_summnodes_config: VectorDriverConfig = field(default_factory=lambda: SUMMNODES_VDB_DEFAULT_DRIVER_CONFIG)
    embedder_config: EmbedderModelConfig = field(default_factory=lambda: EmbedderModelConfig())

    treedb_config: TreeDriverConfig = field(default_factory=lambda: TREE_DB_DEFAULT_DRIVER_CONFIG)

    adriver_config: AgentDriverConfig = field(default_factory=lambda: AgentDriverConfig())
    nodes_summarization_task_config: AgentTaskSolverConfig

    e2n_dist_threshold: float = 0.5
    depth_temp: float = 0.3
    nodes_aggregation_mechanism: str = "sequencial" # "sequencial" | "parallel"

    log: Logger = field(default_factory=lambda: Logger(NODESTREE_MODEL_LOG_PATH))
    verbose: bool = False


class NodesTreeModel:
    def __init__(self, config: NodesTreeModelConfig = NodesTreeModelConfig(), cache_kvdriver_config: KeyValueDriverConfig = None):
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

    def expand_tree(self, triplets: List[Triplet], status_bar: bool = True):

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
        self.log(f"В {len(triplets)} триплетах ({len(triplets)*2} вершин) содержится {len(object_nodes)} \
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

        self.log(f"all/unique/existed nodes - {len(triplets)*2}/{len(object_nodes)}/{len(existed_node_ids)}", verbose=self.config.verbose)
        # TODO : идентификаторы вершин-агрегаторов, которые были обновлены
        return {'nodes': added_node_ids}

    def add_node(self, new_node_strid: str, new_node_text: str) -> ReturnStatus:
        status = ReturnStatus.success

        # проверка вершины, на существование в дереве
        if self.treedb_conn.leaf_exist(new_node_strid):
            status = ReturnStatus.already_exist
            return status

        # Поиск parent-вершины, к которой будет добавлена новая child-вершина
        traversed_nodes_ids, parent_node = self.traverse_tree(new_node_text)

        # вызов llm для перегенерации summary-вершин
        nodes_new_summaries = self.summarize_path_nodes(traversed_nodes_ids, new_node_text)

        # обновление/добвавление summarize-вершин в соответствующую векторную бд
        self.update_vectordb_info(traversed_nodes_ids, nodes_new_summaries)

        # обновить информацию в summarize-вершинах в соответствующей графовой бд
        self.update_treedb_info(traversed_nodes_ids, nodes_new_summaries,
                                new_node_strid, parent_node)

        # прикрепить новую child-вершину к выбранной parent-вершине в дереве
        self.attach_node_to_tree(parent_node.id, new_node_text, {'str_id': new_node_strid})

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
            child_nodes = self.traverse_tree.get_child_nodes(parent_node_id)

            # Оцениваем семантическое расстояние между child-вершинами (с типом leaf) и newnode_text
            leaf_nodes = list(filter(lambda node: node.type == TreeNodeType.leaf, child_nodes))
            strid2leafid_map = {node.prop['str_id']: node.id for node in leaf_nodes}
            leaf_nodes_strids = list(strid2leafid_map.keys())
            if len(leaf_nodes_strids) > 0:
                raw_scored_leafnodes = self.vectordb_leafnodes_conn.retrieve(
                    query_instances=[newnode_vinstance], n_results=len(leaf_nodes_strids),
                    subset_ids=leaf_nodes_strids, includes=[])[0]
                scored_leafnodes = list(map(lambda pair: (pair[0], strid2leafid_map[pair[1].id]), raw_scored_leafnodes))
            else:
                scored_leafnodes = []

            # Оцениваем семантическое расстояние между child-вершинами (с типом summarized) и newnode_text
            summ_nodes = list(filter(lambda node: node.type == TreeNodeType.summarized, child_nodes))
            summ_nodes_ids = list(map(lambda node: node.id, summ_nodes))
            if len(summ_nodes_ids) > 0:
                raw_scored_summnodes = self.vectordb_summnodes_conn.retrieve(
                    query_instances=[newnode_vinstance], n_results=len(summ_nodes_ids),
                    subset_ids=summ_nodes_ids, includes=[])[0]
                scored_summnodes = list(map(lambda pair: (pair[0], strid2leafid_map[pair[1].id]), raw_scored_summnodes))
            else:
                scored_summnodes = []

            # Выполняем фильтрацию child-вершин на основании их семантического расстояния к newnode_text
            # по адаптивному пороговому значению
            adaptive_threshold = self.config.e2n_dist_threshold * np.exp(self.config.depth_temp*cur_depth)
            filtered_child_nodes = list(filter(lambda scored_node: scored_node[0] < adaptive_threshold, scored_leafnodes + scored_summnodes))

            # Если после фильтрации не осталось ни одной вершины, в которую можно выполнить переход,
            # то завершаем обход дерева, иначе выбираем самую семантически-близкую вершину в качестве
            # следующей parent-вершины.
            if len(filtered_child_nodes) < 1:
                parent_node = self.treedb_conn.read([parent_node_id])[0]
                stop_flag = True
            else:
                sorted_child_nodes = sorted(filtered_child_nodes, key=lambda p: p[0], reverse=False)
                parent_node_id = sorted_child_nodes[0][1]
                traversed_nodes_ids.append(parent_node_id)
                cur_depth += 1

        return parent_node, traversed_nodes_ids

    def summarize_path_nodes(self, traversed_nodes_ids: List[str], newnode_text: str) -> List[Tuple[int, str]]:
        nodes_new_summaries = []
        for node_id in traversed_nodes_ids[::-1]:
            curparent_node = self.treedb_conn.read([node_id])[0]
            parent_text = curparent_node.text
            parent_descendants_num = curparent_node.prop['descendants_num']

            if self.config.nodes_aggregation_mechanism == 'sequencial':
                prev_summ_text = newnode_text if len(nodes_new_summaries) < 1 else nodes_new_summaries[-1][1]
                summ_text = self.nodes_summarization_solver.solve(
                    parent_text=parent_text, new_child_text=prev_summ_text,
                    descendants_num=parent_descendants_num)

            elif self.config.nodes_aggregation_mechanism == 'parallel':
                summ_text = self.nodes_summarization_solver.solve(
                    parent_ntext=parent_text, new_child_ntext=newnode_text,
                    descendants_num=parent_descendants_num)

            else:
                raise ValueError

            nodes_new_summaries.append((parent_descendants_num+1, summ_text))
        return nodes_new_summaries[::-1]

    def update_vectordb_info(self, ids: List[str], new_texts: List[str]) -> None:
        torch.cuda.empty_cache()
        embs = self.embedder.encode_passages(new_texts, batch_size=16)
        formated_instances = [VectorDBInstance(id=id, document=doc, embedding=emb, metadata={'id': id})
                            for id, doc, emb in zip(ids, new_texts, embs)]
        self.vectordb_summnodes_conn.create(formated_instances)

    def update_treedb_info(self, ids: List[str], texts: List[str], new_node_strid: str, parent_node: TreeNode) -> None:
        if len(ids) > 1:
            # У всех summarized-вершин обновляем значения text- и descendants_num-полей
            for node_id, new_text in zip(ids[:-1],texts[:-1]):
                cur_node = self.treedb_conn.read([node_id])[0]
                cur_node.text = new_text
                cur_node.prop['descendants_num'] += 1
                cur_node.prop['aggregated_str_ids'].append(new_node_strid)
                self.treedb_conn.update(cur_node)

            # Eсли последняя вершина имеет тип leaf, то меняем её тип на summarized,
            # добавляем descendants_num-поле и удаляем str_id-поле
            if parent_node.type == TreeNodeType.leaf:
                self.treedb_conn.change_node_type_to_summarized(id=ids[-1], new_text=texts[-1])

                # перевешиваем leaf-вершину, на переформатированную summarized-вершину
                self.attach_node_to_tree(parent_node.id, parent_node.text, parent_node.props)

    def attach_node_to_tree(id: str, node_text: str, props: Dict[str, object]) -> None:
        # TODO
        pass

    def match_entitie2nodes(self, entitie: str):
        pass
        # TODO
        # сущности сопоставляется общая вершина (информацией об обших подвершинах и базовых object-нодах)

    def reduce_tree(self, triplets: List[Triplet], delete_info: Dict[int, Dict[str, bool]]):
        # TODO
        pass

    def count_items(self):
        return {
            'tree': self.treedb_conn.count_items(),
            'vector_basenodes': self.vectordb_leafnodes_conn.count_items(),
            'vector_summnodes': self.vectordb_summnodes_conn.count_items()}

    def clear(self):
        self.vectordb_leafnodes_conn.clear()
        self.vectordb_summnodes_conn.clear()
        self.treedb_conn.clear()
