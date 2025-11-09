from dataclasses import dataclass, field
from typing import Tuple, List, Dict, Union
from copy import deepcopy

from .config import E2NMATCHER_MAIN_LOG_PATH, E2NM_RERANKDRIVER_DEFAULT_CONFIG
from ......kg_model import KnowledgeGraphModel
from ......utils import ReturnInfo, Logger
from ......utils.errors import ReturnStatus
from ......utils.data_structs import NodeType, BaseComponentConfig, NodeInfo
from ......db_drivers.kv_driver import KeyValueDriverConfig
from ......utils.cache_kv import CacheUtils
from ......rerankers import RerankerDriverConfig, RerankerDriver
from ......utils.cache_kv.CacheOperations import CacheOperations


@dataclass
class Entities2NodesMatcherConfig(BaseComponentConfig):
    """Конфигурация Entities2NodesMatcher-стадии MediumQA-ризонера.

    :param use_tree: Если True, то для сопоставления сущностей с object-вершинами из графа будет использована древовидная модель представления вершин из графа знаний, иначе для matching-операции будет использован Retrieve/Rerank-оператор. Значение по умолчанию False.
    :type use_tree: str, optional
    :param reranker_driver_config: Конфигурация Retrieve/Rerank-оператора. Значение по умолчанию E2NM_RERANKDRIVER_DEFAULT_CONFIG.
    :type reranker_driver_config: Union[Dict,RerankerDriverConfig], optional
    :param max_n: Максимальное количество вершин из графа знаний, которе может быть сопоставлено одной сущности. Значение по умолчанию 3.
    :type max_n: int, optional
    :param cache_table_name: Название таблицы в структуре (базе) данных, куда будут сохраняться (кешироваться) основные результаты работы Entities2NodesMatcher-класса. Значение по умолчанию 'medreasn_e2nmatcher_main_stage_cache'.
    :type cache_table_name: str, optional
    """
    use_tree: bool = False
    reranker_driver_config: Union[Dict, RerankerDriverConfig] = field(default_factory=lambda: E2NM_RERANKDRIVER_DEFAULT_CONFIG)
    max_n: int = 3

    cache_table_name: str = "medreasn_e2nmatcher_main_stage_cache"
    log: Logger = field(default_factory=lambda: Logger(E2NMATCHER_MAIN_LOG_PATH))

    def to_str(self):
        return f"{self.use_tree}|{self.max_n}|{self.reranker_driver_config.to_str()}"

    @staticmethod
    def from_dict(dict_config: Dict):
        dictconfig_copy = deepcopy(dict_config)
        formated_config = Entities2NodesMatcherConfig(**dictconfig_copy)
        formated_config.formate_fields()
        return formated_config

    def formate_fields(self):
        if isinstance(self.reranker_driver_config, dict):
            self.reranker_driver_config = RerankerDriverConfig.from_dict(self.reranker_driver_config)
        else:
            self.reranker_driver_config.formate_fields()


class Entities2NodesMatcher(CacheUtils, CacheOperations):
    """Верхнеуровневый класс стадии #2.1.2 medium QA-конвейера для выполнения сопоставоения сущностей из user-вопроса с вершинами в графе знаний.

    :param kg_model: Модель памяти (графа знаний) ассистента.
    :type kg_model: KnowledgeGraphModel
    :param config: Конфигурация Entities2NodesMatcher-стадии. Значение по умолчанию Entities2NodesMatcherConfig().
    :type config: Union[Entities2NodesMatcherConfig. Dict], optional
    :param cache_kvdriver_config: Конфигурация структуры данных для кеширования промежуточных результатов в рамках компонент данного класса. Значение по умолчению None.
    :type cache_kvdriver_config: Union[KeyValueDriverConfig, None], optional
    """

    def __init__(self, kg_model: KnowledgeGraphModel, config: Union[Entities2NodesMatcherConfig, Dict] = Entities2NodesMatcherConfig(),
                 cache_kvdriver_config: Union[None, KeyValueDriverConfig] = None):
        if isinstance(config, dict):
            config: Entities2NodesMatcherConfig = Entities2NodesMatcherConfig.from_dict(config)
        else:
            config.formate_fields()
        self.config = config

        self.kg_model = kg_model

        self.cachekv = self.init_cachekv(
            cache_kvdriver_config, config.cache_table_name)

        self.retriever = RerankerDriver.specify(
            self.config.reranker_driver_config,
            kg_model.graph_embeddings.nodes_vcomposers[NodeType.object])

        self.log = self.config.log
        self.verbose = self.config.verbose

    def get_cache_key(self, entitie: str) -> List[object]:
        return [entitie, self.config.to_str()]

    @CacheUtils.cache_method_output
    def match_entitie2knowledge(self, entitie: str) -> List[NodeInfo]:
        if self.config.use_tree:
            matched_objects = self.kg_model.nodestree_model.match_entitie2objects(entitie, max_n=self.config.max_n)
        else:
            matched_objects = list(map(
                lambda node: NodeInfo(id=node.id, text=node.document, type=NodeType.object),
                self.retriever.run(entitie, top_k=self.config.max_n, includes=['documents'])
            ))

        return matched_objects

    def perform(self, entities: List[str]) -> Tuple[Dict[str, List[NodeInfo]], ReturnInfo]:
        """Метод предназначен для сопоставления заданных сущностей (на естественном языке) с вершинами из графа знаний.

        :param entities: Список сущностей.
        :type entities: List[str]
        :rtype: Tuple[Dict[str,List[NodeInfo]], ReturnInfo]
        """
        self.log("START ENTITIES2NODES MATCHING...", verbose=self.config.verbose)
        self.log(f"ENTIITES: {entities}", verbose=self.config.verbose)
        if len(entities) < 1:
            raise ValueError
        rinfo = ReturnInfo()

        matched_kg_objects: Dict[str, List[NodeInfo]] = dict()
        for i, entitie in enumerate(entities):
            self.log(f"Текушая сушность #{i}: {entitie}", verbose=self.verbose)
            matched_kg_objects[entitie] = self.match_entitie2knowledge(entitie)
            str_matchedobjects = ', '.join(list(map(lambda obj: obj.text, matched_kg_objects[entitie])))
            self.log(f"RESULT: {str_matchedobjects}", verbose=self.verbose)

        m_objects_amount = sum(list(map(lambda m_objects: len(m_objects), matched_kg_objects.values())))
        if m_objects_amount < 1:
            rinfo.status = ReturnStatus.empty_answer
        self.log(f"STATUS: {rinfo.status}", verbose=self.verbose)

        return matched_kg_objects, rinfo
