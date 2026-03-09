from typing import List, Dict, Set, Union, Tuple
from dataclasses import dataclass, field
from copy import deepcopy
from collections import defaultdict
from time import time

from .config import KG_MAIN_LOG_PATH, DEFAULT_AGENTS_MAP, DEFAULT_EMBEDDERS_MAP, \
    DEFAULT_AGENTS_CONFIG, DEFAULT_EMBEDDERS_CONFIG
from .graph_model.GraphModel import GraphModelConfig, GraphModel
from .embeddings_model.EmbeddingsModel import EmbeddingsModelConfig, EmbeddingsModel
from .nodestree_model import NodesTreeModelConfig, NodesTreeModel
from .utils import AgentsMapping, KGEmbeddersMapping
from ..db_drivers.kv_driver import KeyValueDriverConfig
from ..db_drivers.vector_driver.embedders import EmbedderModel, EmbedderModelConfig
from ..agents import AgentDriverConfig, AgentDriver
from ..utils import Triplet, Logger, accumulate_step_info, ReturnInfo
from ..utils.data_structs import RelationType, NodeType, NodeInfo, BaseComponentConfig


@dataclass
class KnowledgeGraphModelConfig(BaseComponentConfig):
    """Конфигурация памяти (граф знаний) ассистента.

    :param graph_struct_config: Конфигурация структуры данных, которая отвечает за хранение знаний ассистента в формате графа. Значение по умолчанию GraphModelConfig().
    :type graph_struct_config: Union[Dict,GraphModelConfig], optional
    :param graph_embeddings_config: Конфигурация структуры данных, которая отвечает за представление/хранение знаний ассистента в векторном формате. Значение по умолчанию EmbeddingsModelConfig().
    :type graph_embeddings_config: Union[Dict,EmbeddingsModelConfig], optional
    :param nodestree_config: Конфигурация структуры данных, которая отвечает за представление/хранение знаний (object-вершин) ассистента в формате дерева. Значение по умолчанию None.
    :type nodestree_config: Union[NodesTreeModelConfig,Dict,None], optional
    :param embedders_configs: Словарь с именованными (ключи) конфигурациями embedder-моделей (значения) для векторизации текста, которые будут использоваться в рамках Memorize- и QA-пайплайнов для построения графа знаний и осуществления поиска. Значение по умолчанию DEFAULT_EMBEDDERS_CONFIG.
    :type embedders_configs: Dict[str, Union[Dict,EmbedderModelConfig]], optional
    :param embedders_map: Вложенный именованный словарь с указанием PersonalAI-компоненты (ключ) и ключевого слова/имени (значение) embedder-конфигурации из embedders_configs-поля, которая будет использоваться в её рамках. Значение по умолчанию DEFAULT_EMBEDDERS_MAP.
    :type embedders_map: Union[Dict,KGEmbeddersMapping], optional
    :param agents_configs: Словарь с именованными (ключи) конфигурациями LLM-агентов (значения) для выполнения inferece-операций, которые будут использоваться в рамках Memorize- и QA-пайплайнов для построения графа знаний и осуществления поиска. Значение по умолчанию DEFAULT_AGENTS_CONFIG.
    :type agents_configs: Dict[str, Union[Dict,AgentDriverConfig]], optional
    :param agents_map: Вложенный именованный словарь с указанием PersonalAI-компоненты и её подчастей (ключ) и ключевого слова/имени (значение) конфигураци LLM-агента из agents_configs-поля, которая будет использоваться в её рамках. Значение по умолчанию DEFAULT_AGENTS_MAP.
    :type agents_map: Union[Dict,AgentsMapping], optional
    """
    graph_struct_config: Union[Dict, GraphModelConfig] = field(default_factory=lambda: GraphModelConfig())
    graph_embeddings_config: Union[Dict, EmbeddingsModelConfig] = field(default_factory=lambda: EmbeddingsModelConfig())
    nodestree_config: Union[NodesTreeModelConfig, Dict, None] = None

    embedders_configs: Dict[str, Union[Dict, EmbedderModelConfig]] = field(default_factory=lambda: DEFAULT_EMBEDDERS_CONFIG)
    embedders_map: Union[Dict, KGEmbeddersMapping] = field(default_factory=lambda: DEFAULT_EMBEDDERS_MAP)

    agents_configs: Dict[str, Union[Dict, AgentDriverConfig]] = field(default_factory=lambda: DEFAULT_AGENTS_CONFIG)
    agents_map: Union[Dict, AgentsMapping] = field(default_factory=lambda: DEFAULT_AGENTS_MAP)

    log_path: str = KG_MAIN_LOG_PATH

    def to_str(self):
        # TODO
        raise NotImplementedError

    @staticmethod
    def from_dict(dict_config):
        dictconfig_copy = deepcopy(dict_config)
        formated_config = KnowledgeGraphModelConfig(**dictconfig_copy)
        formated_config.formate_fields()
        return formated_config

    def formate_fields(self):
        if isinstance(self.graph_struct_config, dict):
            self.graph_struct_config = GraphModelConfig.from_dict(self.graph_struct_config)
        else:
            self.graph_struct_config.formate_fields()

        if isinstance(self.graph_embeddings_config, dict):
            self.graph_embeddings_config = EmbeddingsModelConfig.from_dict(self.graph_embeddings_config)
        else:
            self.graph_embeddings_config.formate_fields()

        if isinstance(self.nodestree_config, dict):
            self.nodestree_config = NodesTreeModelConfig.from_dict(self.nodestree_config)
        elif self.nodestree_config is not None:
            self.nodestree_config.formate_fields()

        for emb_name, emb_config in self.embedders_configs.items():
            if isinstance(emb_config, dict):
                self.embedders_configs[emb_name] = EmbedderModelConfig.from_dict(emb_config)
            else:
                self.embedders_configs[emb_name].formate_fields()

        if isinstance(self.embedders_map, dict):
            self.embedders_map = KGEmbeddersMapping(**self.embedders_map)

        for agent_name, agent_config in self.agents_configs.items():
            if isinstance(agent_config, dict):
                self.agents_configs[agent_name] = AgentDriverConfig.from_dict(agent_config)
            else:
                self.agents_configs[agent_name].formate_fields()

        if isinstance(self.agents_map, dict):
            self.agents_map = AgentsMapping(**self.agents_map)


class KnowledgeGraphModel:
    """Модель памяти (граф знаний) ассистента.

    :param config: Конфигурация памяти (граф знаний) ассистента. Значение по умолчанию KnowledgeGraphModelConfig().
    :type config: Union[Dict,KnowledgeGraphModelConfig], optional
    :param cache_kvdriver_config: Конфигурация структуры данных для кеширования промежутчных результатов в рамках компонент данного класса. Значение по умолчанию None.
    :type cache_kvdriver_config: Union[KeyValueDriverConfig, None], optional
    """

    def __init__(self, config: Union[Dict, KnowledgeGraphModelConfig] = KnowledgeGraphModelConfig(),
                 cache_kvdriver_config: Union[KeyValueDriverConfig, None] = None) -> None:
        if isinstance(config, dict):
            config: KnowledgeGraphModelConfig = KnowledgeGraphModelConfig.from_dict(config)
        else:
            config.formate_fields()

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
        self.log = Logger(config.log_path)
        self.verbose = config.verbose
        self.log_level = config.log_level

    def check_consistency(self) -> bool:
        """Метод проверяет согласованность внутренних представлений памяти (графовой, векторной и, при наличии, nodestree-модели).
        В случае критичных несоответствий вызываются исключения (assert), а также пишутся подробные сообщения в лог.

        :return: True, если проверка завершилась успешно и критичные несоответствия не были обнаружены.
        :rtype: bool
        """
        self.log.debug("CHECKING KNOWLEDGEGRAPH CONSISTENCY...", verbose=self.verbose, log_level=self.log_level)
        self.graph_embeddings.check_consistency()

        gdb_count = self.graph_struct.db_conn.count_items(detailed=True)
        self.log.debug("* Graph-db status: %s .", gdb_count, verbose=self.verbose, log_level=self.log_level)

        vdb_nodes_count: Dict[str, Dict[str, int]] = dict()
        for node_type, v_composer in self.graph_embeddings.nodes_vcomposers.items():
            vdb_nodes_count[node_type.value] = v_composer.count_items()
        vdb_triplets_count = self.graph_embeddings.triplets_vcomposer.count_items()
        self.log.debug("* Vector nodes-db status: %s .", vdb_nodes_count, verbose=self.verbose, log_level=self.log_level)
        self.log.debug("* Vector triples-db status: %s .", vdb_triplets_count, verbose=self.verbose, log_level=self.log_level)

        for n_type, graph_n_count in gdb_count['nodes'].items():
            for _, vector_n_count in vdb_nodes_count[n_type].items():
                assert graph_n_count == vector_n_count

        for _, vector_t_count in vdb_triplets_count.items():
            assert sum(gdb_count['triplets'].values()) >= vector_t_count

        if self.nodestree_model is not None:
            self.nodestree_model.check_consistency()

        return True

    def check_createinfo(self, triplets: List[Triplet], create_info: Dict[str, Dict[str, Union[Dict[Union[RelationType, NodeType], Set[str]], Set[str]]]]) -> None:
        """Метод сопоставляет информацию из create_info с фактически добавленными объектами в графовой и векторной структурах.

        :param triplets: Список триплетов, которые были добавлены в память.
        :type triplets: List[Triplet]
        :param create_info: Структура с информацией о созданных объектах в графовой и векторной частях памяти.
        :type create_info: Dict[str, Dict[Union[RelationType, NodeType], Set[str]]]
        :return: None
        :rtype: None
        """
        self.log.debug("CHECKING CREATEINFO...", verbose=self.verbose, log_level=self.log_level)

        # 0. created, but not existed objects in graph and embeddings structures
        nexisted_graph_tids = defaultdict(set)
        for t_type, t_ids in create_info['graph_info']['triplets'].items():
            for t_id in t_ids:
                tid_exist = self.graph_struct.db_conn.item_exist(t_id, id_type='triplet')
                if not tid_exist:
                    nexisted_graph_tids[t_type].add(t_id)
        self.log.debug("Created but not existed Triplets (Relations) in graph structure:", verbose=self.verbose, log_level=self.log_level)
        nexisted_gtids_count = {k: len(v) for k, v in nexisted_graph_tids.items()}
        self.log.debug("* Count: %s .", nexisted_gtids_count, verbose=self.verbose, log_level=self.log_level)
        self.log.debug("* Ids: %s .", nexisted_graph_tids, verbose=self.verbose, log_level=self.log_level)

        nexisted_graph_nids = defaultdict(set)
        for n_type, n_ids in create_info['graph_info']['nodes'].items():
            for n_id in n_ids:
                nid_exist = self.graph_struct.db_conn.item_exist(NodeInfo(id=n_id, type=n_type), id_type='node')
                if not nid_exist:
                    nexisted_graph_nids[n_type].add(n_id)
        self.log.debug("Created but not existed Nodes in graph structure:", verbose=self.verbose, log_level=self.log_level)
        nexisted_gnids_count = {k: len(v) for k, v in nexisted_graph_nids.items()}
        self.log.debug("* Count: %s .", nexisted_gnids_count, verbose=self.verbose, log_level=self.log_level)
        self.log.debug("* ids: %s .", nexisted_graph_nids, verbose=self.verbose, log_level=self.log_level)

        nexisted_embd_rids = set()
        for r_id in create_info['embeddings_info']['triplets']:
            rid_exist = self.graph_embeddings.triplets_vcomposer.item_exist(id=r_id)
            if not rid_exist:
                nexisted_embd_rids.add(r_id)
        self.log.debug("Created but not existed Triplets in embeddings structure:", verbose=self.verbose, log_level=self.log_level)
        self.log.debug("* Count: %d .", len(nexisted_embd_rids), verbose=self.verbose, log_level=self.log_level)
        self.log.debug("* Ids: %s .", nexisted_embd_rids, verbose=self.verbose, log_level=self.log_level)

        nexisted_embd_nids = defaultdict(set)
        for n_type, n_ids in create_info['embeddings_info']['nodes'].items():
            for n_id in n_ids:
                nid_exist = self.graph_embeddings.nodes_vcomposers[n_type].item_exist(id=n_id)
                if not nid_exist:
                    nexisted_embd_nids[n_type].add(n_id)
        nexisted_embd_nids = dict(nexisted_embd_nids)
        self.log.debug("Created but not existed Nodes in embeddings structure:", verbose=self.verbose, log_level=self.log_level)
        self.log.debug("* Count: %d .", len(nexisted_embd_nids), verbose=self.verbose, log_level=self.log_level)
        self.log.debug("* Ids: %s .", nexisted_embd_nids, verbose=self.verbose, log_level=self.log_level)

        # 1. для каждой вершины, добавленной в графовую структуру, должен быть соответствующий ембеддинг, добавленный в векторную структуру
        lefted_graph_n_ids = deepcopy(create_info['graph_info']['nodes'])
        lefted_emb_n_ids = deepcopy(create_info['embeddings_info']['nodes'])
        for n_type, graph_n_typed_ids in create_info['graph_info']['nodes'].items():
            matched_emb_n_ids = lefted_emb_n_ids.get(n_type, set()).intersection(graph_n_typed_ids)
            lefted_graph_n_ids[n_type] = lefted_graph_n_ids[n_type].difference(matched_emb_n_ids)

            lefted_emb_n_ids[n_type] = lefted_emb_n_ids[n_type].difference(graph_n_typed_ids)

        self.log.debug("Graph Nodes without corresponding embeddings: %s .",
                       lefted_graph_n_ids, verbose=self.verbose, log_level=self.log_level)
        self.log.debug("Nodes Embeddings without representation in graph structure: %s .",
                       lefted_emb_n_ids, verbose=self.verbose, log_level=self.log_level)

        # 2. если добавляется simple-связи в графовую структуру, то должен быть соответствующий ембеддинг, добавленный в векторную структуру
        embtid_to_graphtid = dict()
        graphtid_to_embtid = dict()
        for triplet in triplets:
            if triplet.relation.type == RelationType.simple:
                if triplet.id in create_info['graph_info']['triplets'][RelationType.simple]:
                    graphtid_to_embtid[triplet.id] = triplet.relation.id if triplet.relation.id in create_info['embeddings_info']['triplets'] else None

                if triplet.relation.id in create_info['embeddings_info']['triplets']:
                    embtid_to_graphtid[triplet.relation.id] = triplet.id if triplet.id in create_info['graph_info']['triplets'][RelationType.simple] else None

        lefted_graph_simple_t_ids = set(map(lambda pair: pair[0], filter(lambda pair: pair[1] is None, graphtid_to_embtid.items())))
        lefted_emb_simple_t_ids = set(map(lambda pair: pair[0], filter(lambda pair: pair[1] is None, embtid_to_graphtid.items())))
        self.log.debug("Graph Simple-triplets (Relations) without corresponding embeddings: %s .",
                       lefted_graph_simple_t_ids, verbose=self.verbose, log_level=self.log_level)
        self.log.debug("Simple-triplet (Relation) Embeddings without representation in graph structure: %s .",
                       lefted_emb_simple_t_ids, verbose=self.verbose, log_level=self.log_level)

    def check_deleteinfo(self, triplets: List[Triplet], delete_info: Dict[str, Dict[str, Set[str]]]) -> None:
        self.log.debug("CHEKING DELETEINFO...", verbose=self.verbose, log_level=self.log_level)
        # TODO
        pass

    @accumulate_step_info
    def add_knowledge(self, triplets: List[Triplet], check_consistency: bool = True, check_createinfo: bool = False, status_bar: bool = False) -> Tuple[Dict[str, Dict[str, Set[str]]], ReturnInfo, bool]:
        """Метод предназначен для добавления информации в память ассистента в виде списка триплетов.

        :param triplets: Список триплетов с информацией для добавления в память ассистента.
        :type triplets: List[Triplet]
        :param check_consistency: Если True, то после выполнения данной операции будет проверена консистентность памяти ассистента, иначе False. Значение по умолчанию False.
        :type check_consistency: bool, optional
        :param check_createinfo: Если True, то после добавления информации в память выполняется дополнительная проверка структуры create_info на согласованность с переданными триплетами. Если False, проверка не выполняется. Значение по умолчанию False.
        :type check_createinfo: bool, optional
        :param status_bar: Если True, то во время исполнения операции в stdout будет выводиться статус её исполнения, иначе False. Значение по умолчанию True.
        :type status_bar: bool, optional
        :return: Кортеж из трёх объектов: (1) словарь с информацией о триплетах, которые были добавлены в память ассистента; (2) статус завершения операции с пояснительной информацией; (3) True, если результат был получен из кеша (cache hit), иначе False.
        :rtype: Tuple[Dict[str, Dict[str, Set[str]]], ReturnInfo, bool]
        """
        self.log.info("START ADDING KNOWLEDGE TO MEMORY...", verbose=self.verbose, log_level=self.log_level)
        rinfo = ReturnInfo()

        gc_stime = time()
        graph_create_info = self.graph_struct.create_triplets(triplets, status_bar=status_bar)
        gc_etime = time()

        ec_stime = time()
        embd_create_info = self.graph_embeddings.create_triplets(triplets, status_bar=status_bar)
        ec_etime = time()

        # embd_create_info['nodes'] = reduce(lambda acc, v: acc.union(v), list(embd_create_info['nodes'].values()), set())  # костыль

        tc_stime = time()
        if self.nodestree_model is not None:
            tree_expand_info = self.nodestree_model.expand_tree(
                triplets, status_bar=status_bar)
        else:
            tree_expand_info = None
        tc_etime = time()

        create_info = {
            'graph_info': graph_create_info,
            'embeddings_info': embd_create_info,
            'tree_info': tree_expand_info
        }

        self.log.info("RESULT:", verbose=self.verbose, log_level=self.log_level)
        self.log.debug("* Graph create_info: %s .", create_info['graph_info'], verbose=self.verbose, log_level=self.log_level)
        self.log.debug("* Embeddings create_info: %s .", create_info['embeddings_info'], verbose=self.verbose, log_level=self.log_level)
        self.log.debug("* Tree create_info: %s .", create_info['tree_info'], verbose=self.verbose, log_level=self.log_level)
        self.log.info("* Add triples to graph-struct elapsed time: %.5f sec .", gc_etime - gc_stime, verbose=self.verbose, log_level=self.log_level)
        self.log.info("* Add triples to embeddings-struct elapsed time: %.5f sec .", ec_etime - ec_stime, verbose=self.verbose, log_level=self.log_level)
        self.log.info("* Add triples to tree-struct elapsed time: %.5f sec .", tc_etime - tc_stime, verbose=self.verbose, log_level=self.log_level)

        if check_createinfo:
            self.check_createinfo(triplets, create_info)

        if check_consistency:
            self.check_consistency()

        return create_info, rinfo, False

    @accumulate_step_info
    def remove_knowledge(self, triplets: List[Triplet], check_consistency: bool = True, check_deleteinfo: bool = True) -> Tuple[Dict[str, Dict[int, Dict[str, bool]]], ReturnInfo, bool]:
        """Метод предназначен для удаления информации из памяти ассистента.
        Удаление производится по идентификаторам триплетов, в которых данная информация находилась
        при её добавлении в память с помощью соответствующего add_knowledge-метода.

        :param triplets: Набор триплетов, по которым нужно удалить соответствующую информацию из памяти ассистента.
        :type triplets: List[Triplet]
        :param check_consistency: Если True, то после выполнения данной операции будет проверена консистентность памяти ассистента, иначе False. Значение по умолчанию False.
        :type check_consistency: bool, optional
        :return: Кортеж из трёх объектов: (1) словарь с информацией о триплетах, которые были удалены (значение True, иначе False) из памяти ассистента; (2) статус завершения операции с пояснительной информацией; (3) True, если результат был получен из кеша (cache hit), иначе False.
        :rtype: Tuple[Dict[str, Dict[int, Dict[str, bool]]], ReturnInfo, bool]
        """
        rinfo = ReturnInfo()
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

        return delete_info, rinfo, False

    def count_items(self, detailed: bool = False) -> Dict[str, Dict[str, int]]:
        """Возвращает агрегированную статистику по количеству объектов в памяти. Для каждой компоненты памяти вычисляется отдельная статистика.

        :param detailed: Если True, возвращаются детализированные статистики по типам узлов и триплетов. Если False, может быть возвращено только общее количество объектов (в зависимости от реализации конкретных коннекторов).
        :type detailed: bool, optional
        :return: Словарь с ключами 'graph_info', 'embeddings_info', 'nodestree_info'  и соответствующими статистиками.
        :rtype: Dict[str, Dict[str, int]]
        """
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
        """Очищает KV-кеши, связанные с моделью памяти, в зависимости от заданного уровня.

        :param level: Режим очистки KV-кэшей: 'all', 'current' или 'other'.
        :type level: str
        :return: None
        :rtype: None
        """
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

    def close_connections(self):
        for a_name in self.AVAILABLE_AGENTS.keys():
            self.AVAILABLE_AGENTS[a_name].close_connection()
        self.graph_embeddings.close_connections()
        self.graph_struct.close_connections()
        if self.nodestree_model is not None:
            self.nodestree_model.close_connections()
