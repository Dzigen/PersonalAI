from typing import List, Dict, Set, Union
from dataclasses import dataclass, field
import gc

from .config import KG_MAIN_LOG_PATH, DEFAULT_AGENTS_MAP, DEFAULT_EMBEDDERS_MAP, \
    DEFAULT_AGENTS_CONFIG, DEFAULT_EMBEDDERS_CONFIG
from .graph_model.GraphModel import GraphModelConfig, GraphModel
from .embeddings_model.EmbeddingsModel import EmbeddingsModelConfig, EmbeddingsModel
from .nodestree_model import NodesTreeModelConfig, NodesTreeModel
from ..db_drivers.kv_driver import KeyValueDriverConfig
from ..db_drivers.vector_driver.embedders import EmbedderModel, EmbedderModelConfig
from ..agents import AgentDriverConfig, AgentDriver
from ..utils import Triplet, Logger


@dataclass
class KnowledgeGraphModelConfig:
    """Конфигурация памяти (граф знаний) ассистента.

    :param graph_struct_config: Конфигурация структуры данных, которая отвечает за хранение знаний ассистента в формате графа. Значение по умолчанию GraphModelConfig().
    :type graph_struct_config: GraphModelConfig, optional
    :param graph_embeddings_config: Конфигурация структуры данных, которая отвечает за представление/хранение знаний ассистента в векторном формате. Значение по умолчанию EmbeddingsModelConfig().
    :type graph_embeddings_config: EmbeddingsModelConfig, optional
    :param nodestree_config: Конфигурация структуры данных, которая отвечает за представление/хранение знаний ассистента в формате дерева. Значение по умолчанию None.
    :type nodestree_config: Union[NodesTreeModelConfig,None], optional
    :param embedders_configs: Словарь с именованными (ключи) конфигурациями embedder-моделей (значения) для векторизации текста, которые будут использоваться в рамках Memorize- и QA-пайплайнов для построения графа знаний и осуществления поиска. Значение по умолчанию DEFAULT_EMBEDDERS_CONFIG.
    :type embedders_configs: Dict[str, EmbedderModelConfig], optional
    :param agents_configs: Словарь с именованными (ключи) конфигурациями LLM-агентов (значения) для выполнения inferece-операций, которые будут использоваться в рамках Memorize- и QA-пайплайнов для построения графа знаний и осуществления поиска. Значение по умолчанию DEFAULT_AGENTS_CONFIG.
    :type agents_configs: Dict[str, AgentDriverConfig], optional
    :param embedders_map: Вложенный именованный словарь с указанием PersonalAI-компоненты и её подчастей (ключ) и ключевого слова/имени (значение) embedder-конфигурации, которая будет использоваться в её рамках. Значение по умолчанию DEFAULT_EMBEDDERS_MAP.
    :type embedders_map: Dict[str, Dict], optional
    :param agents_map: Вложенный именованный словарь с указанием PersonalAI-компоненты и её подчастей (ключ) и ключевого слова/имени (значение) конфигураци LLM-агента, которая будет использоваться в её рамках. Значение по умолчанию DEFAULT_AGENTS_MAP.
    :type agents_map: Dict[str, Dict], optional
    :param log: Отладочный класс для журналирования/мониторинга поведения инициализируемой компоненты. Значение по умолчанию Logger(KG_MAIN_LOG_PATH).
    :type log: Logger
    :param verbose: Если True, то информация о поведении класса будет сохраняться в stdout и файл-журналирования (log), иначе только в файл. Значение по умолчанию False.
    :type verbose: bool
    """
    graph_struct_config: GraphModelConfig = field(default_factory=lambda: GraphModelConfig())
    graph_embeddings_config: EmbeddingsModelConfig = field(default_factory=lambda: EmbeddingsModelConfig())
    nodestree_config: Union[NodesTreeModelConfig, None] = None

    # :param embedder_config: Конфигурация класса, отвечающего за приведения текста в его векторное представление с помощью заданной embedder-модели. Значение по умолчанию EmbedderModelConfig().
    # :type embedder_config: EmbedderModelConfig, optional

    embedders_config: Dict[str, EmbedderModelConfig] = field(default_factory=lambda: DEFAULT_EMBEDDERS_CONFIG)
    agents_config: Dict[str, AgentDriverConfig] = field(default_factory=lambda: DEFAULT_AGENTS_CONFIG)
    embedders_map: Dict[str, Dict] = field(default_factory=lambda: DEFAULT_EMBEDDERS_MAP)
    agents_map: Dict[str, Dict] = field(default_factory=lambda: DEFAULT_AGENTS_MAP)

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

        self.AVAILABLE_EMBEDDERS = {emb_name: EmbedderModel(emb_config) for emb_name, emb_config in config.embedders_config.items()}
        self.AVAILABLE_AGENTS = {agent_name: AgentDriver.connect(agent_config) for agent_name, agent_config in config.agents_config.items()}

        self.EMBEDDERS_MAP = config.embedders_map
        self.AGENTS_MAP = config.agents_map

        self.graph_struct = GraphModel(config.graph_struct_config)

        self.graph_embeddings = EmbeddingsModel(
            self.AVAILABLE_EMBEDDERS[self.EMBEDDERS_MAP['KnowledgeGraphModel']['EmbeddingsModel']],
            config.graph_embeddings_config)

        self.nodestree_model = None
        if config.nodestree_config is not None:
            self.nodestree_model = NodesTreeModel(
                self.AVAILABLE_AGENTS[self.AGENTS_MAP['KnowledgeGraphModel']['NodesTreeModel']],
                self.AVAILABLE_EMBEDDERS[self.EMBEDDERS_MAP['KnowledgeGraphModel']['NodesTreeModel']],
                config.nodestree_config, cache_kvdriver_config)

        self.log = config.log
        self.verbose = config.verbose

    def check_consistency(self) -> bool:
        gdb_count = self.graph_struct.db_conn.count_items()
        self.log(f"GRAPH DB STATUS: {gdb_count}", verbose=self.verbose)
        vdb_nodes_count = self.graph_embeddings.vectordbs['nodes'].count_items()
        vdb_triplets_count = self.graph_embeddings.vectordbs['triplets'].count_items()
        self.log(
            f"VECTOR DB STATUS: {vdb_nodes_count} - nodes; {vdb_triplets_count} - triplets", verbose=self.verbose)

        assert gdb_count['nodes'] == vdb_nodes_count
        assert gdb_count['triplets'] >= vdb_triplets_count
        # assert vdb_nodes_count > vdb_triplets_count

        if self.nodestree_model is not None:
            self.nodestree_model.check_consistency()

        return True

    def add_knowledge(self, triplets: List[Triplet], check_consistency: bool = True, status_bar: bool = False) -> Dict[str, Dict[str, Set[str]]]:
        """Метод предназначен для добавления информации в память ассистента в виде списка триплетов.

        :param triplets: Список триплетов с информацией для добавления в память ассистента.
        :type triplets: List[Triplet]
        :param check_consistency: Если True, то после выполнения данной операции будет проверена консистентность памяти ассистента, иначе False. Значение по умолчанию True.
        :type check_consistency: bool, optional
        :param status_bar: Если True, то во время исполнения операции в stdout будет выводиться статус её исполнения, иначе False. Значение по умолчанию True.
        :type status_bar: bool, optional
        :return: Словарь с информацией о триплетах, которые были добавлены в память ассистента.
        :rtype: Dict[str, Dict[str,Set[str]]]
        """
        graph_create_info = self.graph_struct.create_triplets(
            triplets, status_bar=status_bar)
        embd_create_info = self.graph_embeddings.create_triplets(
            triplets, status_bar=status_bar)

        if self.nodestree_model is not None:
            tree_expand_info = self.nodestree_model.expand_tree(
                triplets, status_bar=status_bar)
        else:
            tree_expand_info = None

        if check_consistency:
            self.check_consistency()

        return {'graph_info': graph_create_info, 'embeddings_info': embd_create_info, 'tree_info': tree_expand_info}

    def remove_knowledge(self, triplets: List[Triplet], check_consistency: bool = True) -> Dict[str, Dict[int, Dict[str, bool]]]:
        """Метод предназначен для удаления информации из памяти ассистента.
        Удаление производится по идентификаторам триплетов, в которых данная информация находилась
        при её добавлении в память с помощью соответствующего add_knowledge-метода.

        :param triplets: Набор триплетов, по которым нужно удалить соответствующую информацию из памяти ассистента.
        :type triplets: List[Triplet]
        :param check_consistency: Если True, то после выполнения данной операции будет проверена консистентность памяти ассистента, иначе False. Значение по умолчанию True.
        :type check_consistency: bool, optional
        :return: Словарь с информацией о триплетах, которые были удалены (значение True, иначе False) из памяти ассистента.
        :rtype: Dict[str, Dict[int,Dict[str,bool]]]
        """
        graph_delete_info, embds_delete_info = self.graph_struct.delete_triplets(
            triplets)
        self.graph_embeddings.delete_triplets(
            triplets, delete_info=embds_delete_info)

        if self.nodestree_model is not None:
            tree_reduce_info = self.nodestree_model.reduce_tree(
                triplets, delete_info=graph_delete_info)
        else:
            tree_reduce_info = None

        if check_consistency:
            self.check_consistency()

        return {'graph_info': graph_delete_info, 'embeddings_info': embds_delete_info, 'tree_info': tree_reduce_info}

    def count_items(self) -> Dict[str, Dict[str, int]]:
        return {
            'graph_info': self.graph_struct.count_items(),
            'embeddings_info': self.graph_embeddings.count_items(),
            'nodestree_info': self.nodestree_model.count_items() if self.nodestree_model is not None else None
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
        del self.graph_struct
        del self.graph_embeddings
        if self.nodestree_model is not None:
            del self.nodestree_model
        gc.collect()
