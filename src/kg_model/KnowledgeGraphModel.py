from typing import List, Dict, Set, Union
from dataclasses import dataclass, field
import gc
from functools import reduce
from copy import deepcopy
from collections import defaultdict

from .config import KG_MAIN_LOG_PATH, DEFAULT_AGENTS_MAP, DEFAULT_EMBEDDERS_MAP, \
    DEFAULT_AGENTS_CONFIG, DEFAULT_EMBEDDERS_CONFIG
from .graph_model.GraphModel import GraphModelConfig, GraphModel
from .embeddings_model.EmbeddingsModel import EmbeddingsModelConfig, EmbeddingsModel
from .nodestree_model import NodesTreeModelConfig, NodesTreeModel
from .utils import AgentsMapping, KGEmbeddersMapping
from ..db_drivers.kv_driver import KeyValueDriverConfig
from ..db_drivers.vector_driver.embedders import EmbedderModel, EmbedderModelConfig
from ..agents import AgentDriverConfig, AgentDriver
from ..utils import Triplet, Logger
from ..utils.data_structs import RelationType, NodeType, NodeInfo


@dataclass
class KnowledgeGraphModelConfig:
    """Конфигурация памяти (граф знаний) ассистента.

    :param graph_struct_config: Конфигурация структуры данных, которая отвечает за хранение знаний ассистента в формате графа. Значение по умолчанию GraphModelConfig().
    :type graph_struct_config: GraphModelConfig, optional
    :param graph_embeddings_config: Конфигурация структуры данных, которая отвечает за представление/хранение знаний ассистента в векторном формате. Значение по умолчанию EmbeddingsModelConfig().
    :type graph_embeddings_config: EmbeddingsModelConfig, optional
    :param nodestree_config: Конфигурация структуры данных, которая отвечает за представление/хранение знаний (object-вершин) ассистента в формате дерева. Значение по умолчанию None.
    :type nodestree_config: Union[NodesTreeModelConfig,None], optional
    :param embedders_configs: Словарь с именованными (ключи) конфигурациями embedder-моделей (значения) для векторизации текста, которые будут использоваться в рамках Memorize- и QA-пайплайнов для построения графа знаний и осуществления поиска. Значение по умолчанию DEFAULT_EMBEDDERS_CONFIG.
    :type embedders_configs: Dict[str, EmbedderModelConfig], optional
    :param embedders_map: Вложенный именованный словарь с указанием PersonalAI-компоненты (ключ) и ключевого слова/имени (значение) embedder-конфигурации из embedders_configs-поля, которая будет использоваться в её рамках. Значение по умолчанию DEFAULT_EMBEDDERS_MAP.
    :type embedders_map: KGEmbeddersMapping, optional
    :param agents_configs: Словарь с именованными (ключи) конфигурациями LLM-агентов (значения) для выполнения inferece-операций, которые будут использоваться в рамках Memorize- и QA-пайплайнов для построения графа знаний и осуществления поиска. Значение по умолчанию DEFAULT_AGENTS_CONFIG.
    :type agents_configs: Dict[str, AgentDriverConfig], optional
    :param agents_map: Вложенный именованный словарь с указанием PersonalAI-компоненты и её подчастей (ключ) и ключевого слова/имени (значение) конфигураци LLM-агента из agents_configs-поля, которая будет использоваться в её рамках. Значение по умолчанию DEFAULT_AGENTS_MAP.
    :type agents_map: AgentsMapping, optional
    :param log: Отладочный класс для журналирования/мониторинга поведения инициализируемой компоненты. Значение по умолчанию Logger(KG_MAIN_LOG_PATH).
    :type log: Logger
    :param verbose: Если True, то информация о поведении класса будет сохраняться в stdout и файл-журналирования (log), иначе только в файл. Значение по умолчанию False.
    :type verbose: bool
    """
    graph_struct_config: GraphModelConfig = field(default_factory=lambda: GraphModelConfig())
    graph_embeddings_config: EmbeddingsModelConfig = field(default_factory=lambda: EmbeddingsModelConfig())
    nodestree_config: Union[NodesTreeModelConfig, None] = None

    embedders_configs: Dict[str, EmbedderModelConfig] = field(default_factory=lambda: DEFAULT_EMBEDDERS_CONFIG)
    embedders_map: KGEmbeddersMapping = field(default_factory=lambda: DEFAULT_EMBEDDERS_MAP)

    agents_configs: Dict[str, AgentDriverConfig] = field(default_factory=lambda: DEFAULT_AGENTS_CONFIG)
    agents_map: AgentsMapping = field(default_factory=lambda: DEFAULT_AGENTS_MAP)

    log: Logger = field(default_factory=lambda: Logger(KG_MAIN_LOG_PATH))
    verbose: bool = False


class KnowledgeGraphModel:
    """Модель памяти (граф знаний) ассистента.

    :param config: Конфигурация памяти (граф знаний) ассистента. Значение по умолчанию KnowledgeGraphModelConfig().
    :type config: KnowledgeGraphModelConfig, optional
    :param cache_kvdriver_config: Конфигурация структуры данных для кеширования промежутчных результатов в рамках компонент данного класса. Значение по умолчению None.
    :type cache_kvdriver_config: Union[KeyValueDriverConfig, None], optional
    """

    def __init__(self, config: KnowledgeGraphModelConfig = KnowledgeGraphModelConfig(),
                 cache_kvdriver_config: Union[KeyValueDriverConfig, None] = None) -> None:
        self.AVAILABLE_EMBEDDERS = {emb_name: EmbedderModel(emb_config) for emb_name, emb_config in config.embedders_configs.items()}
        self.AVAILABLE_AGENTS = {agent_name: AgentDriver.connect(agent_config) for agent_name, agent_config in config.agents_configs.items()}
        self.KG_EMBEDDERS_MAP: KGEmbeddersMapping = config.embedders_map
        self.AGENTS_MAP: AgentsMapping = config.agents_map

        self.graph_struct = GraphModel(config.graph_struct_config)

        self.graph_embeddings = EmbeddingsModel(
            {db_name: self.AVAILABLE_EMBEDDERS[emb_name] for db_name, emb_name in self.KG_EMBEDDERS_MAP.embeddings_model.items()},
            config.graph_embeddings_config)

        self.nodestree_model = None
        if config.nodestree_config is not None:
            self.nodestree_model = NodesTreeModel(
                self.AVAILABLE_AGENTS[self.AGENTS_MAP.kg_nodestree_model],
                {db_name: self.AVAILABLE_EMBEDDERS[emb_name] for db_name, emb_name in self.KG_EMBEDDERS_MAP.nodestree_model.items()},
                config.nodestree_config, cache_kvdriver_config)

        self.cache_config = cache_kvdriver_config
        self.log = config.log
        self.verbose = config.verbose

    def check_consistency(self) -> bool:
        self.log("Checking KnowledgeGraph consistency...", verbose=self.verbose)
        self.graph_embeddings.check_consistency()

        gdb_count = self.graph_struct.db_conn.count_items(detailed=True)
        self.log(f"GRAPH DB STATUS: {gdb_count}", verbose=self.verbose)

        vdb_nodes_count: Dict[str, Dict[str, int]] = dict()
        for node_type, v_composer in self.graph_embeddings.nodes_vcomposers.items():
            vdb_nodes_count[node_type.value] = v_composer.count_items()
        vdb_triplets_count = self.graph_embeddings.triplets_vcomposer.count_items()
        self.log(f"VECTOR NODES DB STATUS: {vdb_nodes_count}", verbose=self.verbose)
        self.log(f"VECTOR TRIPLETS DB STATUS: {vdb_triplets_count}", verbose=self.verbose)

        for n_type, graph_n_count in gdb_count['nodes'].items():
            for _, vector_n_count in vdb_nodes_count[n_type].items():
                assert graph_n_count == vector_n_count

        for _, vector_t_count in vdb_triplets_count.items():
            assert sum(gdb_count['triplets'].values()) >= vector_t_count

        if self.nodestree_model is not None:
            self.nodestree_model.check_consistency()

        return True

    def check_createinfo(self, triplets: List[Triplet], create_info: Dict[str, Dict[str, Union[Dict[Union[RelationType, NodeType], Set[str]], Set[str]]]]) -> None:
        self.log("Checking CreateInfo...", verbose=self.verbose)

        # 0. created, but not existed objects in graph and embeddings structures
        nexisted_graph_tids = defaultdict(set)
        for t_type, t_ids in create_info['graph_info']['triplets'].items():
            for t_id in t_ids:
                tid_exist = self.graph_struct.db_conn.item_exist(t_id, id_type='triplet')
                if not tid_exist:
                    nexisted_graph_tids[t_type].add(t_id)
        self.log(f"Created but not existed Triplets (Relations) in graph structure:", verbose=self.verbose)
        nexisted_gtids_count = {k: len(v) for k, v in nexisted_graph_tids.items()}
        self.log(f"- count: {nexisted_gtids_count}", verbose=self.verbose)
        self.log(f"- ids: {nexisted_graph_tids}", verbose=self.verbose)

        nexisted_graph_nids = defaultdict(set)
        for n_type, n_ids in create_info['graph_info']['nodes'].items():
            for n_id in n_ids:
                nid_exist = self.graph_struct.db_conn.item_exist(NodeInfo(id=n_id, type=n_type), id_type='node')
                if not nid_exist:
                    nexisted_graph_nids[n_type].add(n_id)
        self.log(f"Created but not existed Nodes in graph structure:", verbose=self.verbose)
        nexisted_gnids_count = {k: len(v) for k, v in nexisted_graph_nids.items()}
        self.log(f"- count: {nexisted_gnids_count}", verbose=self.verbose)
        self.log(f"- ids: {nexisted_graph_nids}", verbose=self.verbose)

        nexisted_embd_rids = set()
        for r_id in create_info['embeddings_info']['triplets']:
            rid_exist = self.graph_embeddings.triplets_vcomposer.item_exist(id=r_id)
            if not rid_exist:
                nexisted_embd_rids.add(r_id)
        self.log(f"Created but not existed Triplets in embeddings structure: [{len(nexisted_embd_rids)}] {nexisted_embd_rids}", verbose=self.verbose)

        nexisted_embd_nids = defaultdict(set)
        for n_type, n_ids in create_info['embeddings_info']['nodes'].items():
            for n_id in n_ids:
                nid_exist = self.graph_embeddings.nodes_vcomposers[n_type].item_exist(id=n_id)
                if not nid_exist:
                    nexisted_embd_nids[n_type].add(n_id)
        nexisted_embd_nids = dict(nexisted_embd_nids)
        self.log(f"Created but not existed Nodes in embeddings structure: [{len(nexisted_embd_nids)}] {nexisted_embd_nids}", verbose=self.verbose)

        # 1. для каждой вершины, добавленной в графовую структуру, должен быть соответствующий ембеддинг, добавленный в векторную структуру
        lefted_graph_n_ids = deepcopy(create_info['graph_info']['nodes'])
        lefted_emb_n_ids = deepcopy(create_info['embeddings_info']['nodes'])
        for n_type, graph_n_typed_ids in create_info['graph_info']['nodes'].items():
            matched_emb_n_ids = lefted_emb_n_ids.get(n_type, set()).intersection(graph_n_typed_ids)
            lefted_graph_n_ids[n_type] = lefted_graph_n_ids[n_type].difference(matched_emb_n_ids)

            lefted_emb_n_ids[n_type] = lefted_emb_n_ids[n_type].difference(graph_n_typed_ids)

        self.log(f"Graph Nodes without corresponding embeddings: {lefted_graph_n_ids}", verbose=self.verbose)
        self.log(f"Nodes Embeddings without representation in graph structure: {lefted_emb_n_ids}", verbose=self.verbose)

        # 2. если добавляется simple-связи в графовую структуру, то должен быть соответствующий ембеддинг, добавленный в векторную структуру
        embtid_to_graphtid = dict()
        graphtid_to_embtid = dict()
        for triplet in triplets:
            if triplet.relation.type == RelationType.simple:
                if triplet.id in create_info['graph_info']['triplets'][RelationType.simple]:
                    graphtid_to_embtid[triplet.id] = triplet.relation.id if triplet.relation.id in create_info['embeddings_info']['triplets'] else None

                if triplet.relation.id in create_info['embeddings_info']['triplets']:
                    embtid_to_graphtid[triplet.relation.id] = triplet.id if triplet.id in create_info['graph_info']['triplets'][RelationType.simple] else None

        lefted_emb_simple_t_ids = set(map(lambda pair: pair[0], filter(lambda pair: pair[1] is None, embtid_to_graphtid.items())))
        lefted_graph_simple_t_ids = set(map(lambda pair: pair[0], filter(lambda pair: pair[1] is None, graphtid_to_embtid.items())))
        self.log(f"Graph Simple-triplets (Relations) without corresponding embeddings: {lefted_graph_simple_t_ids}", verbose=self.verbose)
        self.log(f"Simple-triplet (Relation) Embeddings without representation in graph structure: {lefted_emb_simple_t_ids}", verbose=self.verbose)

    def check_deleteinfo(self, triplets: List[Triplet], delete_info: Dict[str, Dict[str, Set[str]]]) -> None:
        self.log("Checking DeleteInfo...", verbose=self.verbose)
        # TODO
        pass

    def add_knowledge(self, triplets: List[Triplet], check_consistency: bool = True, check_createinfo: bool = False, status_bar: bool = False) -> Dict[str, Dict[str, Set[str]]]:
        """Метод предназначен для добавления информации в память ассистента в виде списка триплетов.

        :param triplets: Список триплетов с информацией для добавления в память ассистента.
        :type triplets: List[Triplet]
        :param check_consistency: Если True, то после выполнения данной операции будет проверена консистентность памяти ассистента, иначе False. Значение по умолчанию False.
        :type check_consistency: bool, optional
        :param status_bar: Если True, то во время исполнения операции в stdout будет выводиться статус её исполнения, иначе False. Значение по умолчанию True.
        :type status_bar: bool, optional
        :return: Словарь с информацией о триплетах, которые были добавлены в память ассистента.
        :rtype: Dict[str, Dict[str,Set[str]]]
        """
        graph_create_info = self.graph_struct.create_triplets(triplets, status_bar=status_bar)
        embd_create_info = self.graph_embeddings.create_triplets(triplets, status_bar=status_bar)

        # embd_create_info['nodes'] = reduce(lambda acc, v: acc.union(v), list(embd_create_info['nodes'].values()), set())  # костыль

        if self.nodestree_model is not None:
            tree_expand_info = self.nodestree_model.expand_tree(
                triplets, status_bar=status_bar)
        else:
            tree_expand_info = None

        create_info = {
            'graph_info': graph_create_info,
            'embeddings_info': embd_create_info,
            'tree_info': tree_expand_info
        }
        self.log(f"CREATE INFO: {create_info}", verbose=self.verbose)
        if check_createinfo:
            self.check_createinfo(triplets, create_info)

        if check_consistency:
            self.check_consistency()

        return create_info

    def remove_knowledge(self, triplets: List[Triplet], check_consistency: bool = True, check_deleteinfo: bool = True) -> Dict[str, Dict[int, Dict[str, bool]]]:
        """Метод предназначен для удаления информации из памяти ассистента.
        Удаление производится по идентификаторам триплетов, в которых данная информация находилась
        при её добавлении в память с помощью соответствующего add_knowledge-метода.

        :param triplets: Набор триплетов, по которым нужно удалить соответствующую информацию из памяти ассистента.
        :type triplets: List[Triplet]
        :param check_consistency: Если True, то после выполнения данной операции будет проверена консистентность памяти ассистента, иначе False. Значение по умолчанию False.
        :type check_consistency: bool, optional
        :return: Словарь с информацией о триплетах, которые были удалены (значение True, иначе False) из памяти ассистента.
        :rtype: Dict[str, Dict[int,Dict[str,bool]]]
        """
        graph_delete_info, embds_delete_info = self.graph_struct.delete_triplets(triplets)
        self.graph_embeddings.delete_triplets(triplets, delete_info=embds_delete_info)

        if self.nodestree_model is not None:
            tree_reduce_info = self.nodestree_model.reduce_tree(
                triplets, delete_info=graph_delete_info)
        else:
            tree_reduce_info = None

        delete_info = {
            'graph_info': graph_delete_info,
            'embeddings_info': embds_delete_info,
            'tree_info': tree_reduce_info
        }

        if check_deleteinfo:
            # TODO
            pass

        if check_consistency:
            self.check_consistency()

        return delete_info

    def count_items(self, detailed: bool = False) -> Dict[str, Dict[str, int]]:
        return {
            'graph_info': self.graph_struct.count_items(detailed),
            'embeddings_info': self.graph_embeddings.count_items(detailed),
            'nodestree_info': self.nodestree_model.count_items(detailed) if self.nodestree_model is not None else None
        }

    def clear(self) -> None:
        """Метод предназначен для полного удаления содержимого памяти ассистента.
        """
        self.graph_embeddings.clear()
        self.graph_struct.clear()
        if self.nodestree_model is not None:
            self.nodestree_model.clear()

    def clear_kv_caches(self, level: str = 'other') -> None:
        if not isinstance(level, str):
            raise TypeError(
                f"Аргумент переменной 'level' должен иметь тип 'str'; сейчас аргумент имеет тип '{type(level)}'")
        if level not in ['all', 'current', 'other']:
            raise ValueError(
                f"Аргумент переменной 'level' должен принимать одно из трёх значенией: 'all', 'current' или 'other'. Полученное значение: '{level}'")

        if level in ['current', 'all']:
            raise NotImplementedError

        if level in ['other']:
            if self.nodestree_model is not None:
                self.nodestree_model.clear_kv_caches()

    def __del__(self):
        try:
            for a_name in self.AVAILABLE_AGENTS.keys():
                self.AVAILABLE_AGENTS[a_name].close_connection()
        except AttributeError:
            pass

        try:
            del self.graph_embeddings
            del self.graph_struct
            if self.nodestree_model is not None:
                del self.nodestree_model
        except AttributeError:
            pass

        gc.collect()
