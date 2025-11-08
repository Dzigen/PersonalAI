####
# Author:   Mikhail Menschikov
# Email:    menshikov.mikhail.2001@gmail.com
# Created:  22.04.2025
# Source paper: https://arxiv.org/pdf/2410.14052
####

from dataclasses import dataclass
from dataclasses import dataclass, field
from typing import List, Dict, Set, Union, Tuple
import numpy as np
from tqdm import tqdm
from copy import deepcopy
import gc
from time import time

from .utils import NodesTreeModelAgentTasksConfig, NodesTreeModelTaskSolvers
from .config import NODESTREE_MODEL_LOG_PATH, \
    LEAFNODES_VDB_DEFAULT_DRIVER_CONFIGS_MAPPING, SUMMNODES_VDB_DEFAULT_DRIVER_CONFIGS_MAPPING, \
    TREE_DB_DEFAULT_DRIVER_CONFIG, LNT_RERANKDRIVER_DEFAULT_CONFIG, SNT_RERANKDRIVER_DEFAULT_CONFIG
from ...db_drivers.tree_driver.utils import TreeNodeType, TreeNode, TreeIdType
from ...utils import Logger, AgentTaskSolver, ReturnStatus
from ...utils.data_structs import Triplet, NodeType, create_id, Node, NodeInfo, BaseComponentConfig, LanguageConfig
from ...utils.errors import ReturnStatus
from ...utils.agent_stat_analyzer import AgentStatAnalyzerConfig
from ...agents.utils import AbstractAgentConnector
from ...db_drivers.kv_driver import KeyValueDriverConfig
from ...db_drivers.vector_driver import VectorDriverConfig, VectorDBInstance, VectorComposer
from ...db_drivers.tree_driver import TreeDriver, TreeDriverConfig
from ...db_drivers.vector_driver.embedders import EmbedderModel
from ...rerankers import RerankerDriver, RerankerDriverConfig
from ...utils.cache_kv.CacheOperations import CacheOperations
from ...utils.agent_stat_analyzer.AgentStatOperations import AgentStatOperations


@dataclass
class NodesTreeModelConfig(BaseComponentConfig, LanguageConfig):
    """Конфигурация древовидной структуры данных для хранения object-вершин.

    :param leafnodes_vdb_driver_configs_mapping: Именованные конфигурации баз данных для хранения различных векторных представлений leaf-объектов (object-вершин) дерева. Значение по умолчанию LEAFNODES_VDB_DEFAULT_DRIVER_CONFIGS_MAPPING.
    :type leafnodes_vdb_driver_configs_mapping: Dict[str, Union[Dict,VectorDriverConfig]], optional
    :param leafnodes_reranker_driver_config: Конфигурация Retrieve/Rerank-оператора для векторной бд с leaf-вершинами (вершинами типа object из графовой структуры данных). Значение по умолчанию LNT_RERANKDRIVER_DEFAULT_CONFIG.
    :type leafnodes_reranker_driver_config: Union[Dict,RerankerDriverConfig], optional

    :param summnodes_vdb_driver_configs_mapping: Именованные конфигурации баз данных для хранения различных векторных представлений parent-объектов (summarized-вершин) дерева. Значение по умолчанию SUMMNODES_VDB_DEFAULT_DRIVER_CONFIG.
    :type summnodes_vdb_driver_configs_mapping: Dict[str, Union[Dict,VectorDriverConfig]], optional
    :param summnodes_reranker_driver_config: Конфигурация Retrieve/Rerank-оператора для векторной бд с summarized-вершинами. Значение по умолчанию SNT_RERANKDRIVER_DEFAULT_CONFIG.
    :type summnodes_reranker_driver_config: Union[Dict,RerankerDriverConfig], optional

    :param treedb_config: Конфигурация графовой базы данных для хранения древовидного представления object-вершин. Значение по умолчанию TREE_DB_DEFAULT_DRIVER_CONFIG.
    :type treedb_config: Union[Dict,TreeDriverConfig], optional

    :param agent_gen_stategy: Стратегия генерации текста для используемого LLM-агента. В случае None-значение будет использоваться стратегия по умолчанию. Значение по умолчанию None.
    :type agent_gen_stategy: Union[None,Dict[str, str]], optional
    :param agent_tasks_config: Конфигурации LLM-промптом для решения заданных задач с помощью LLM-агента. Значение по умолчанию NodesTreeModelAgentTasksConfig().
    :type agent_tasks_config: Union[Dict,NodesTreeModelAgentTasksConfig], optional

    :param e2n_base_threshold: Служебный гиперпараметр; см. https://arxiv.org/pdf/2410.14052. Значение по умолчанию 0.4.
    :type e2n_base_threshold: float, optional
    :param depth_rate: Служебный гиперпараметр; см. https://arxiv.org/pdf/2410.14052. Значение по умолчанию 0.5.
    :type depth_rate: float, optional
    :param nodes_aggregation_mechanism: Служебный гиперпараметр; см. https://arxiv.org/pdf/2410.14052. Значение по умолчанию 'sequencial'.
    :type nodes_aggregation_mechanism: str, optional
    """

    leafnodes_vdb_driver_configs_mapping: Dict[str, Union[Dict, VectorDriverConfig]] = field(
        default_factory=lambda: LEAFNODES_VDB_DEFAULT_DRIVER_CONFIGS_MAPPING)
    leafnodes_reranker_driver_config: Union[Dict, RerankerDriverConfig] = field(
        default_factory=lambda: LNT_RERANKDRIVER_DEFAULT_CONFIG)

    summnodes_vdb_driver_configs_mapping: Dict[str, Union[Dict, VectorDriverConfig]] = field(
        default_factory=lambda: SUMMNODES_VDB_DEFAULT_DRIVER_CONFIGS_MAPPING)
    summnodes_reranker_driver_config: Union[Dict, RerankerDriverConfig] = field(
        default_factory=lambda: SNT_RERANKDRIVER_DEFAULT_CONFIG)

    treedb_config: Union[Dict, TreeDriverConfig] = field(
        default_factory=lambda: TREE_DB_DEFAULT_DRIVER_CONFIG)

    agent_gen_stategy: Union[None, Dict[str, str]] = None
    agent_tasks_config: Union[Dict, NodesTreeModelAgentTasksConfig] = field(default_factory=lambda: NodesTreeModelAgentTasksConfig())

    # expanding-tree params
    e2n_base_threshold: float = 0.3
    depth_rate: float = 0.4
    nodes_aggregation_mechanism: str = 'sequencial'  # "sequencial" | "parallel"

    log: Logger = field(default_factory=lambda: Logger(NODESTREE_MODEL_LOG_PATH))
    verbose: bool = False

    def to_str(self):
        # TODO
        raise NotImplementedError

    @staticmethod
    def from_dict(dict_config: Dict):
        formated_config = NodesTreeModelConfig(**dict_config)
        formated_config.formate_fields()
        return formated_config

    def formate_fields(self):
        for vdb_name, vdb_config in self.leafnodes_vdb_driver_configs_mapping.items():
            if isinstance(vdb_config, dict):
                self.leafnodes_vdb_driver_configs_mapping[vdb_name] = VectorDriverConfig.from_dict(vdb_config)
            else:
                self.leafnodes_vdb_driver_configs_mapping[vdb_name].formate_fields()

        if isinstance(self.leafnodes_reranker_driver_config, dict):
            self.leafnodes_reranker_driver_config = RerankerDriverConfig.from_dict(self.leafnodes_reranker_driver_config)
        else:
            self.leafnodes_reranker_driver_config.formate_fields()

        for vdb_name, vdb_config in self.summnodes_vdb_driver_configs_mapping.items():
            if isinstance(vdb_config, dict):
                self.summnodes_vdb_driver_configs_mapping[vdb_name] = VectorDriverConfig.from_dict(vdb_config)
            else:
                self.summnodes_vdb_driver_configs_mapping[vdb_name].formate_fields()

        if isinstance(self.summnodes_reranker_driver_config, dict):
            self.summnodes_reranker_driver_config = RerankerDriverConfig.from_dict(self.summnodes_reranker_driver_config)
        else:
            self.summnodes_reranker_driver_config.formate_fields()

        if isinstance(self.treedb_config, dict):
            self.treedb_config = TreeDriverConfig.from_dict(self.treedb_config)
        else:
            self.treedb_config.formate_fields()

        if isinstance(self.agent_tasks_config, dict):
            self.agent_tasks_config = NodesTreeModelAgentTasksConfig.from_dict(self.agent_tasks_config)
        else:
            self.agent_tasks_config.formate_fields()


class NodesTreeModel(CacheOperations, AgentStatOperations):
    """Класс предназначен для представления object-вершин из графовой структуры данных в виде дерева с целью
    повышения эффективности сопоставления имеющихся занний с сущностями/запросами из поступающих user-вопросов.

    :param agent: Коннектор к конкретному LLM-агенту для выполнения inference-операций.
    :type agent: AbstractAgentConnector
    :param embedder: Коннектор к конкретной embedder-моделе для получения векторных представлений текста.
    :type embedder: EmbedderModel
    :param config: Конфигурация NodesTree-модели. Значение по умолчанию NodesTreeModelConfig().
    :type config: Union[Dict,NodesTreeModelConfig], optional
    :param cache_kvdriver_config: Конфигурация структуры данных для кеширования промежуточных результатов в рамках компонент данного класса. Значение по умолчению None.
    :type cache_kvdriver_config: KeyValueDriverConfig, optional
    :param inferencestat_config: Конфигурация компоненты для сбора информации и расчёта статистик по результатам выполнения inference-операциий в рамках LLM-задач. Значение по умолчанию None.
    :type inferencestat_config: Union[None, AgentStatAnalyzerConfig], optional
    :param cache_llm_inference: Если True, то все результаты решения атомарных LLM-задач будут кешироваться, иначе False. Значение по умолчанию True.
    :type cache_llm_inference: bool, optional
    """

    def __init__(self, agent: AbstractAgentConnector, embedders_mapping: Dict[str, EmbedderModel],
                 config: Union[Dict, NodesTreeModelConfig] = NodesTreeModelConfig(),
                 cache_kvdriver_config: Union[None, KeyValueDriverConfig] = None,
                 inferencestat_config: Union[None, AgentStatAnalyzerConfig] = None,
                 cache_llm_inference: bool = True) -> None:
        if isinstance(config, dict):
            config: NodesTreeModelConfig = NodesTreeModelConfig.from_dict(config)
        else:
            config.formate_fields()
        self.config = config
        self.config.agent_tasks_config.versions_to_configs()

        self.treedb_conn = TreeDriver.connect(self.config.treedb_config)

        #
        self.leafnodes_vcomposer = VectorComposer(
            self.config.leafnodes_vdb_driver_configs_mapping,
            embedders_mapping)
        self.leafnodes_retriever = RerankerDriver.specify(
            self.config.leafnodes_reranker_driver_config,
            self.leafnodes_vcomposer)

        #
        self.summnodes_vcomposer = VectorComposer(
            self.config.summnodes_vdb_driver_configs_mapping,
            embedders_mapping)
        self.summnodes_retriever = RerankerDriver.specify(
            self.config.summnodes_reranker_driver_config,
            self.summnodes_vcomposer)

        #
        self.agent = agent
        agents_cache_config = None
        if cache_llm_inference:
            agents_cache_config = cache_kvdriver_config if cache_llm_inference else None

        self.tasks_solvers: NodesTreeModelTaskSolvers = NodesTreeModelTaskSolvers(
            decompose_classifier_solver=AgentTaskSolver(
                self.agent, self.config.agent_tasks_config.nodes_summarization,
                agents_cache_config, inferencestat_config
            )
        )

        self.stages = None
        self.cachekv = None

        self.log = self.config.log
        self.verbose = self.config.verbose

    def check_consistency(self) -> bool:
        self.treedb_conn.check_consistency()
        self.leafnodes_vcomposer.check_consistency()
        self.summnodes_vcomposer.check_consistency()

        leaf_vnodes_counts = self.leafnodes_vcomposer.count_items()
        summ_vnodes_counts = self.summnodes_vcomposer.count_items()
        tnodes_counts = self.treedb_conn.count_items()

        assert list(leaf_vnodes_counts.values())[0] == tnodes_counts['leaf']
        assert list(summ_vnodes_counts.values())[0] == tnodes_counts['summarized']

        return True

    def extract_unique_nodes(self, triplets: List[Triplet]) -> List[Node]:
        unique_object_nodes = dict()
        for triplet in triplets:
            cur_node = triplet.start_node
            if cur_node.type == NodeType.object:
                unique_object_nodes[cur_node.id] = cur_node

            cur_node = triplet.end_node
            if cur_node.type == NodeType.object:
                unique_object_nodes[cur_node.id] = cur_node
        object_nodes = list(unique_object_nodes.values())
        return object_nodes

    def expand_tree(self, triplets: List[Triplet], status_bar: bool = True) -> Dict[str, Set[str]]:
        """Метод предназначен для добавления object-вершин из заданнного набора триплетов в древовидную модель.

        :param triplets: Набор триплетов, object-вершины из которых необходимо добавить в древовидную модель.
        :type triplets: List[Triplet]
        :param status_bar: Если True, то в stdout будет записываться прогресс выполнения данной операции, иначе False. Значение по умолчанию True.
        :type status_bar: bool, optional
        :return: Словарь с информацией об object-вершинах из заданных триплетов, которые были добавлены в деревовидной моделе и которые уже присутствовали в моделе (и повторно добавлены не были).
        :rtype: Dict[str, Set[str]]
        """
        self.log("Старт операции по добавлению object-вершин из заданных триплетов в дерево...", verbose=self.verbose)

        self.log("1. Отбираем уникальные object-вершины...", verbose=self.verbose)
        object_nodes = self.extract_unique_nodes(triplets)
        self.log(f"1.final | В {len(triplets)} триплетах (всего {len(triplets)*2} вершин) содержится {len(object_nodes)} уникальных (по строковому представлению) object-вершин.", verbose=self.verbose)

        self.log(f"2. Добавляем отобранные object-вершины в дерево ({len(object_nodes)})...", verbose=self.verbose)
        process = tqdm(object_nodes) if status_bar else object_nodes
        existed_node_ids, added_node_ids = [], []
        for node in process:
            status = self.add_node(node.id, node.name)

            if status == ReturnStatus.already_exist:
                existed_node_ids.append(node.id)
            else:
                added_node_ids.append(node.id)

        self.log(f"final | all/unique/existed/added nodes - {len(triplets)*2}/{len(object_nodes)}/{len(existed_node_ids)}/{len(added_node_ids)}", verbose=self.config.verbose)
        return {'existed_nodes': existed_node_ids, 'added_nodes': added_node_ids}

    def add_node(self, new_node_strid: str, new_node_text: str) -> ReturnStatus:
        """Метод предназначен для добавления новой вершины в дерево.

        :param new_node_strid: Идентификатор добавляемой вершины.
        :type new_node_strid: str
        :param new_node_text: Значение текстового поля у добавляемой вершины.
        :type new_node_text: str
        :return: Статус завершения/выполнения данной операции.
        :rtype: ReturnStatus
        """
        status = ReturnStatus.success
        self.log(f"2.1. Информация по текущей вершине: (str_id) - {new_node_strid}; (node_text) - {new_node_text}",
                 verbose=self.verbose)

        self.log(f"2.2. Проверка вершины на существование в дереве...", verbose=self.verbose)
        if self.treedb_conn.item_exist(new_node_strid, id_type=TreeIdType.str):
            self.log("2.final | Текущая вершина в дереве существует. Завершение операции.", verbose=self.verbose)
            status = ReturnStatus.already_exist
            return status
        self.log(f"2.2.1. Текущей вершины в дереве не существует. Продолжение операции...", verbose=self.verbose)

        self.log("2.3. Поиск parent-вершины, к которой будет добавлена новая child-вершина...", verbose=self.verbose)
        s_time = time()
        traversed_nodes_ids, parent_node = self.traverse_tree(new_node_text)
        e_time = time()
        self.log(f"2.3.1. Идентификаторы пройденных вершин (internal_ids): {traversed_nodes_ids}", verbose=self.verbose)
        self.log(f"2.3.2. Выбранная parent-вершина: {parent_node}", verbose=self.verbose)
        self.log(f"2.3.3. Затраченное время: {e_time - s_time} секунд", verbose=self.verbose)

        self.log("2.4. Вызов llm для перегенерации text-полей у пройденных вершин в дереве...", verbose=self.verbose)
        s_time = time()
        new_text_summaries = self.summarize_path_nodes(traversed_nodes_ids, new_node_text)
        e_time = time()
        self.log(f"2.4.1. Обновлённые варианты text-полей у пройдённых вершин: {new_text_summaries}", verbose=self.verbose)
        self.log(f"2.4.2. Затраченное время: {e_time - s_time} секунд", verbose=self.verbose)

        self.log("2.5. Обновление/добвавление summarize-вершин в векторной бд...", verbose=self.verbose)
        s_time = time()
        self.update_vectordb_info(TreeNodeType.summarized, traversed_nodes_ids, new_text_summaries)
        e_time = time()
        self.log(f"2.5.1. Затраченное время: {e_time - s_time} секунд", verbose=self.verbose)

        self.log("2.6. Обновление информации в summarize-вершинах в графовой бд...", verbose=self.verbose)
        s_time = time()
        self.update_treedb_info(traversed_nodes_ids, new_text_summaries, new_node_strid, parent_node)
        e_time = time()
        self.log(f"2.6.1. Затраченное время: {e_time - s_time} секунд", verbose=self.verbose)

        self.log("2.7. Обновление/добвавление leaf-вершин в векторной бд...", verbose=self.verbose)
        self.update_vectordb_info(TreeNodeType.leaf, [new_node_strid], [new_node_text])
        self.log("2.8. Прикрепление новой leaf-вершины к выбранной parent-вершине в дереве...", verbose=self.verbose)
        self.attach_node_to_tree(parent_node.id, new_node_text, {'str_id': new_node_strid, 'depth': len(traversed_nodes_ids) + 1})

        self.log("2.final | Операция по добавлению новой вершины завершена успешно!", verbose=self.verbose)
        return status

    def get_leafnodes_sim_scores(self, anchor_vinstance: VectorDBInstance, leaf_nodes: List[TreeNode]) -> List[Tuple[float, str]]:
        strid2leafid_map = {node.props['str_id']: node.id for node in leaf_nodes}
        leafnodes_strids = list(strid2leafid_map.keys())
        if len(leafnodes_strids) > 0:
            # получаем значения семантической близости [similarity]
            scored_leafnodes = self.leafnodes_retriever.run(
                query=anchor_vinstance.document, top_k=len(leafnodes_strids),
                subset_ids=leafnodes_strids, return_with_scores=True, includes=[])

            leafnodes_info = list(map(lambda pair: (pair[0], strid2leafid_map[pair[1].id]), scored_leafnodes))
        else:
            leafnodes_info = []

        return leafnodes_info

    def get_summnodes_sim_scores(self, anchor_vinstance: VectorDBInstance, summ_nodes: List[TreeNode]) -> List[Tuple[float, str]]:
        summ_nodes_ids = list(map(lambda node: node.id, summ_nodes))
        if len(summ_nodes_ids) > 0:
            # получаем значения семантической близости [similarity]
            scored_summnodes = self.summnodes_retriever.run(
                query=anchor_vinstance.document, top_k=len(summ_nodes_ids),
                subset_ids=summ_nodes_ids, return_with_scores=True, includes=[])

            summnodes_info = list(map(lambda pair: (pair[0], pair[1].id), scored_summnodes))
        else:
            summnodes_info = []

        return summnodes_info

    def calculate_adaptive_threshold(self, cur_depth: int) -> float:
        cur_maxdepth = self.treedb_conn.get_tree_maxdepth()
        adaptive_coeff = 1 if cur_maxdepth < 1 else np.exp(
            (self.config.depth_rate * cur_depth) / cur_maxdepth)
        adaptive_threshold = self.config.e2n_base_threshold * adaptive_coeff
        if adaptive_threshold > 1:
            adaptive_threshold = 0.98
        return adaptive_threshold

    def traverse_tree(self, newnode_text: str) -> Tuple[List[str], TreeNode]:
        """Метод предназначен для получения вершины в древодиной моделе, к которой будет прикреплена новая leaf-вершина
        с newnode_text-значением текстового поля.

        :param newnode_text: Значение текстового поля, представляющее leaf-вершину, которому необходимо найти релевантную parent-вершину в дереве для последующего прикрепления к ней.
        :type newnode_text: str
        :return: Кортеж из двух объектов: (1) Путь (список идентификаторов вершин) в дереве от корня (корневой вершины) до вершины, к которой будет прикреплена новая leaf-вершина; (2) Структура данных с информацие по последней вершине в пройденном пути.
        :rtype: Tuple[List[str], TreeNode]
        """
        self.log("3. Старт алгоритма обхода дерева...", verbose=self.verbose)
        parent_node, traversed_nodes_ids = None, []
        newnode_vinstance = VectorDBInstance(document=newnode_text)
        parent_node_id = self.treedb_conn.root_node_id
        cur_depth = 0

        stop_flag = False
        while not stop_flag:
            self.log(f"3.1. Идентификатор текущей parent-вершины (external_id): {parent_node_id}", verbose=self.verbose)
            self.log(f"3.2. Текущая глубина: {cur_depth}", verbose=self.verbose)
            # Получаем child-вершины для текущей parent-вершины
            child_nodes = self.treedb_conn.get_child_nodes(parent_node_id)
            self.log(f"3.3. Child-вершины для текущей parent-вершины:\n* количество: {len(child_nodes)}\n* вершины: {child_nodes}", verbose=self.verbose)

            # Оцениваем семантическую близость [similarity] между child-вершинами (с типом leaf)
            # у текущей parent-вершины и newnode_text
            leaf_nodes = list(filter(lambda node: node.type == TreeNodeType.leaf, child_nodes))
            scored_leafnodes = self.get_leafnodes_sim_scores(newnode_vinstance, leaf_nodes)
            self.log(f"3.4. Оценки семантической близости [similarity] для leaf-вершин:\n* количество: {len(scored_leafnodes)}\n* вершины: {scored_leafnodes}",
                     verbose=self.verbose)

            # Оцениваем семантическую близость [similarity] между child-вершинами (с типом summarized)
            # у текущей parent-вершины и newnode_text
            summ_nodes = list(filter(lambda node: node.type == TreeNodeType.summarized, child_nodes))
            scored_summnodes = self.get_summnodes_sim_scores(newnode_vinstance, summ_nodes)
            self.log(f"3.5. Оценки семантической близости [similarity] для summarized-вершин:\n* количество: {len(scored_summnodes)}\n* вершины: {scored_summnodes}",
                     verbose=self.verbose)

            # Получем адаптивный порог для фильтрации child-вершин
            adaptive_threshold = self.calculate_adaptive_threshold(cur_depth)
            self.log(f"3.6. Текущее значение адаптивного порогового значения: {adaptive_threshold}", verbose=self.verbose)

            # Выполняем фильтрацию child-вершин на основе их семантической близости к newnode_text
            # по адаптивному пороговому значению
            filtered_child_nodes = list(filter(lambda scored_node: scored_node[0] >= adaptive_threshold, scored_leafnodes + scored_summnodes))
            self.log(f"3.7. Оставшиеся summarized- и leaf-вершины в результате фильтрации:\n* количество: {len(filtered_child_nodes)}\n* вершины: {filtered_child_nodes}", verbose=self.verbose)

            # Если после фильтрации не осталось ни одной вершины, в которую можно выполнить переход,
            # то завершаем обход дерева, иначе выбираем самую семантически-близкую [similarity] вершину в качестве
            # следующей parent-вершины.
            if len(filtered_child_nodes) < 1:
                self.log("3.8. Больше некуда спускаться по дереву. Завершаем операцию.", verbose=self.verbose)
                parent_node = self.treedb_conn.read([parent_node_id])[0]
                self.log(f"3.8.1 Последняя parent-вершина: {parent_node}", verbose=self.verbose)
                stop_flag = True
            else:
                sorted_child_nodes = sorted(filtered_child_nodes, key=lambda p: p[0], reverse=True)
                parent_node_id = sorted_child_nodes[0][1]

                self.log("3.8. Спускаемся на вершину вниз по дереву.", verbose=self.verbose)
                self.log(f"3.8.1 Отсортированные вершины: {sorted_child_nodes}.", verbose=self.verbose)
                self.log(f"3.8.2 Идентификатор следующей parent-вершины: {parent_node_id}", verbose=self.verbose)
                traversed_nodes_ids.append(parent_node_id)
                cur_depth += 1

        self.log("3.final | Обход дерева выполнен успешно.", verbose=self.verbose)
        return traversed_nodes_ids, parent_node

    def summarize_path_nodes(self, traversed_nodes_ids: List[str], newnode_text: str) -> List[str]:
        """Метод предназначен для обобщения текстовых полей у вершин в дереве,
        пройденных при поиске релевантной parent-вершины для прикрепления у ней новой leaf-вершины,
        c обуславливанием на newnode_text-значение новой вершины (предками которой они являются).

        :param traversed_nodes_ids: Список индетификаторов пройденных вершин, начиная от корня дерева.
        :type traversed_nodes_ids: List[str]
        :param newnode_text: Значение текстового поля новой вершины, на которое нужно обуславиливаться при генерации более обобщённых текстовых значений у пройденных вершин в дереве.
        :type newnode_text: str
        :return: Список прегенерированных/обобщённых значений тексовых полей у пройденных traversed_nodes_ids-вершин.
        :rtype: List[str]
        """
        self.log(f"4. Старт алгоритма по суммаризации текста...", verbose=self.verbose)
        self.log(f"4.1.1. Количество текстов для обновления: {len(traversed_nodes_ids)}", verbose=self.verbose)
        self.log(f"4.1.2. newnode_text: '{newnode_text}'", verbose=self.verbose)

        new_text_summaries = []
        for node_id in traversed_nodes_ids[::-1]:
            curparent_node = self.treedb_conn.read(
                [node_id], ids_type=TreeIdType.external)[0]
            parent_text = curparent_node.text
            parent_descendants_num = curparent_node.props.get('descendants_num', 0)
            self.log(f"4.2. Текущая вершина для суммаризациии с newnode_text: {curparent_node}", verbose=self.verbose)

            if self.config.nodes_aggregation_mechanism == 'sequencial':
                prev_summ_text = newnode_text if len(
                    new_text_summaries) < 1 else new_text_summaries[-1]
                summ_text, solve_status = self.tasks_solvers.nodes_summarization_solver.solve(
                    lang=self.config.lang,
                    current_content=parent_text, new_content=prev_summ_text,
                    n_descendants=str(parent_descendants_num))

            elif self.config.nodes_aggregation_mechanism == 'parallel':
                summ_text, solve_status = self.tasks_solvers.nodes_summarization_solver.solve(
                    lang=self.config.lang,
                    current_content=parent_text, new_content=newnode_text,
                    n_descendants=str(parent_descendants_num))

            else:
                raise ValueError

            # Если в процессе парсинга ответа llm-агента возникла ошибка,
            # то выполняем наивную суммаризацию
            if solve_status != ReturnStatus.success:
                self.log("При решении задачи-суммаризации возникла ошибка!", verbose=self.verbose)
                summ_text = f"{parent_text}, {newnode_text}"

            self.log(f"4.3. Новое значение text-поля для текущей вершины: {summ_text}", verbose=self.verbose)
            new_text_summaries.append(summ_text)

        self.log("4.final | Сумаризаация текста выполнена успешно", verbose=self.verbose)
        return new_text_summaries[::-1]

    def update_vectordb_info(self, vecdb_type: TreeNodeType, ids: List[str], new_texts: List[str]) -> None:
        """Метод предназначен для добавления/обновления векторных предтавлений вершин из дерева в векторной базе данных.

        :param vecdb_type: Тип вершин, по которым выполняется обновление информации в векторной бд.
        :type vecdb_type: TreeNodeType
        :param ids: Идентификаторы вершин из дерева, с которыми они будут сохранены в векторную бд.
        :type ids: List[str]
        :param new_texts: Значения текстовых полей, на основе которых будут получены векторные представления для соответствующих вершин.
        :type new_texts: List[str]
        """
        formated_instances = [VectorDBInstance(id=id, document=doc, metadata={'id': id}) for id, doc in zip(ids, new_texts)]

        if vecdb_type == TreeNodeType.summarized:
            self.summnodes_vcomposer.upsert(formated_instances)
        elif vecdb_type == TreeNodeType.leaf:
            self.leafnodes_vcomposer.upsert(formated_instances)
        else:
            raise KeyError

    def update_treedb_info(self, ids: List[str], texts: List[str], new_node_strid: str, parent_node: TreeNode) -> None:
        """Метод предназначен для обновления информации (значений текстовых полей) в вершинах дерева,
        пройденных в результате поиска релевантной parent-вершины для прикрепления новой new_node_strid-вершины к дереву.

        :param ids: Идентификаторые вершин в дереве (включая parent-вершину для новой/добавляемой new_node_strid-вершины), у которых необходимо изменить значения тексовых полей.
        :type ids: List[str]
        :param texts: Новые значения текстовых полей для заданных ids-вершин.
        :type texts: List[str]
        :param new_node_strid: Индентификатор новой вершины, которая в дальнейшей будет прикрепляться к parent_node-вершине.
        :type new_node_strid: str
        :param parent_node: Структура данных с информацией о последней пройденной parent-вершине в ids-списке, к которой в дальнейшем будет выполняться приелрепление ноаой new_node_strid-вершины.
        :type parent_node: TreeNode
        """
        # У всех summarized-вершин обновляем значения text- и других-полей
        for node_id, new_text in zip(ids[:-1], texts[:-1]):
            cur_node = self.treedb_conn.read(
                [node_id], ids_type=TreeIdType.external)[0]
            cur_node.text = new_text
            cur_node.props['descendants_num'] += 1
            # cur_node.props['aggregated_str_ids'].append(new_node_strid)
            self.treedb_conn.update([cur_node])

        # Eсли последняя вершина имеет тип leaf, то меняем её тип на summarized,
        # добавляем descendants_num-поле и удаляем str_id-поле.
        # Исходную leaf-вершину перевешиваем на полученную summarized-вершину.
        if parent_node.type == TreeNodeType.leaf:
            self.change_node_to_summarized(parent_node, new_text=texts[-1])
            self.log(
                "Перевешиваем leaf-вершину, на переформатированную/последнюю summarized-вершину", verbose=self.verbose)
            updated_props = deepcopy(parent_node.props)
            updated_props['depth'] += 1
            self.attach_node_to_tree(ids[-1], parent_node.text, updated_props)

    def attach_node_to_tree(self, pn_id: str, ln_text: str, ln_props: Dict[str, object]) -> None:
        """Метод предназначен для создания новой вершины и прикреплению её к существующей pn_id-вершине в дереве.

        :param pn_id: Идентификатор существующей вершины в дереве.
        :type pn_id: str
        :param ln_text: Значение текстового поля у новой вершины.
        :type ln_text: str
        :param ln_props: Значение дополнительных полей у новой верщины.
        :type ln_props: Dict[str, object]
        """
        new_internal_id = create_id(seed=str(time()))
        leaf_node = TreeNode(id=new_internal_id, text=ln_text,
                             type=TreeNodeType.leaf, props=ln_props)
        self.treedb_conn.create(pn_id, leaf_node)

        parent_node = self.treedb_conn.read(
            [pn_id], ids_type=TreeIdType.external)[0]
        if parent_node.type != TreeNodeType.root:
            parent_node.props['descendants_num'] += 1
            # parent_node.props['aggregated_str_ids'].append(new_internal_id)
            self.treedb_conn.update([parent_node])

    def change_node_to_summarized(self, old_node: TreeNode, new_text: str) -> None:
        """Метод предназначен для изменения типа вершины в дереве на summarized.

        :param old_node: Структура данных с исходной информации о вершину, тип которой необходимо изменить.
        :type old_node: TreeNode
        :param new_text: Новое значение текстовго поля изменяемой вершины.
        :type new_text: str
        """
        # обновляем информацию в соответствующей графовой бд
        node_copy = deepcopy(old_node)

        summarized_node = TreeNode(
            id=node_copy.id, text=new_text, type=TreeNodeType.summarized,
            props=node_copy.props)
        summarized_node.props['descendants_num'] = 0
        # summarized_node.props['aggregated_str_ids'] = []
        del summarized_node.props['str_id']

        self.treedb_conn.update([summarized_node])

    def retrieve_relevant_leafnode(self, entitie_vinstance: VectorDBInstance) -> Union[None, Tuple[float, VectorDBInstance]]:
        raw_best_leafnode = self.leafnodes_retriever.run(
            query=entitie_vinstance.document, top_k=1,
            includes=['documents', 'metadatas'], return_with_scores=True)

        best_leafnode = None
        if len(raw_best_leafnode) > 0:
            best_leafnode = raw_best_leafnode[0]

        self.log(f"Семантически-близкая [similarity] leaf-вершина: {best_leafnode}", verbose=self.verbose)
        return best_leafnode

    def retrieve_relevant_summnode(self, entitie_vinstance: VectorDBInstance) -> Union[None, Tuple[float, VectorDBInstance]]:
        raw_best_summnode = self.summnodes_retriever.run(
            query=entitie_vinstance.document, top_k=1,
            includes=[], return_with_scores=True)

        best_summnode = None
        if len(raw_best_summnode) > 0:
            best_summnode = raw_best_summnode[0]

        self.log(f"Семантически-близкая [similarity] summ-вершина: {best_summnode}", verbose=self.verbose)
        return best_summnode

    def get_leafdescendants_for_summnode(self, entitie_vinstance: VectorDBInstance, best_summnode_id: str, max_n: int) -> List[VectorDBInstance]:
        descendants_leaf_nodes = self.treedb_conn.get_leaf_descendants(
            best_summnode_id, id_type=TreeIdType.external)
        descendants_leaf_strids = list(map(lambda node: node.props['str_id'], descendants_leaf_nodes))

        # Если задано ограничение на максимальное количество вершин,
        # которое может быть сопоставлено summarized-вершине
        if max_n > 0 and len(descendants_leaf_strids) > max_n:
            matched_leafnodes = self.leafnodes_retriever.run(
                query=entitie_vinstance.document, top_k=max_n,
                subset_ids=descendants_leaf_strids, includes=[])
            descendants_leaf_strids = list(map(lambda item: item.id, matched_leafnodes))

        matched_nodes = self.leafnodes_vcomposer.read(
            descendants_leaf_strids, includes=["documents", "metadatas"])
        return matched_nodes

    def match_entitie2objects(self, entitie: str, strategy: str = 'collapsed', max_n: int = 1) -> List[NodeInfo]:
        """Метод предназначен для сопоставления object-вершин (из построенного дерева) заданной сущности (на естественном языке).

        :param entitie:
        :type entitie: Сущность на естественном языке.
        :param strategy: Стратегия обхода дерева для формирования релевантного (сопоставляемого заданной сущности) набора object-вершин. Значение по умолчанию 'collapsed'.
        :type strategy: str, optional
        :param max_n: Максимальное количество object-вершин, которое может быть сопоставлено заданной сущности. Если указано отрицательное значение, то данное ограничение снимается. Значение по умолчанию 1.
        :type max_n: int, optional
        :return: Список сопоставленных object-верщин (с их векторными представлениями).
        :rtype: List[VectorDBInstance]
        """
        self.log(f"Старт алгоритма по сопоставлению заданной '{entitie}'-сущности c вершинами из дерева",
                 verbose=self.verbose)
        if strategy == 'collapsed':
            entitie_vinstance = VectorDBInstance(document=entitie)

            self.log("Извлечение самых релевантных к entitie вершин из leaf-бд...", verbose=self.verbose)
            best_leafnode = self.retrieve_relevant_leafnode(entitie_vinstance)

            self.log("Извлечение самых релевантных к entitie вершин из summarized-бд....", verbose=self.verbose)
            best_summnode = self.retrieve_relevant_summnode(entitie_vinstance)
            if best_leafnode is None and best_summnode is None:
                raise ValueError

            # из них выбирается самая релевантная
            if (best_summnode is not None) and (best_summnode[0] < best_leafnode[0]):
                # в случае, если summarized-вершина семантически ближе к entitie,
                # то ей сопоставляются все её (leaf-вершины) вершиным-потомки
                self.log(f"В качестве самой релевантной выбрана summarized-вершина: {best_summnode}", verbose=self.verbose)
                matched_nodes = list(map(
                    lambda vnode: NodeInfo(id=vnode.id, type=NodeType.object, text=vnode.document),
                    self.get_leafdescendants_for_summnode(entitie_vinstance, best_summnode[1].id, max_n)
                ))
                self.log(f"Summarized-вершине соответствуют следующие leaf-вершины (потомки): количество - {len(matched_nodes)}", verbose=self.verbose)
                for i in range(len(matched_nodes)):
                    self.log(f"- {matched_nodes[i]}", verbose=self.verbose)
            else:
                self.log(f"В качестве самой релевантной выбрана leaf-вершина: {best_leafnode}", verbose=self.verbose)
                matched_nodes: List[NodeInfo] = [NodeInfo(id=best_leafnode[1].id, type=NodeType.object, text=best_leafnode[1].document)]
                self.log(f"- {matched_nodes}", verbose=self.verbose)

        elif strategy == 'traversal':
            # TODO
            raise NotImplementedError
        else:
            raise ValueError

        return matched_nodes

    def reduce_tree(self, triplets: List[Triplet], delete_info: Dict[int, Dict[str, bool]]) -> object:
        # TODO
        raise NotImplementedError

    def count_items(self, detailed: bool = False) -> Dict[str, int]:
        # self.check_consistency()
        vector_lnodes_count = self.leafnodes_vcomposer.count_items()
        if not detailed:
            vector_lnodes_count = list(vector_lnodes_count.values())[0]

        vector_snodes_count = self.summnodes_vcomposer.count_items()
        if not detailed:
            vector_snodes_count = list(vector_snodes_count.values())[0]

        tree_nodes_count = self.treedb_conn.count_items()
        if not detailed:
            tree_nodes_count = sum(tree_nodes_count.values())

        return {
            'tree': tree_nodes_count,
            'vector_leafnodes': vector_lnodes_count,
            'vector_summnodes': vector_snodes_count}

    def clear(self) -> None:
        self.leafnodes_vcomposer.clear()
        self.summnodes_vcomposer.clear()
        self.treedb_conn.clear()

    def __del__(self):
        try:
            self.treedb_conn.close_connection()
            del self.treedb_conn

            del self.leafnodes_vcomposer
            del self.summnodes_vcomposer
        except AttributeError:
            pass
        gc.collect()
