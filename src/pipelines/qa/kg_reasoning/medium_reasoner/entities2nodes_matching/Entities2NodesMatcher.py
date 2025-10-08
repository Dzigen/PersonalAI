from dataclasses import dataclass, field
from typing import Tuple, List, Dict, Union

from .config import E2NMATCHER_MAIN_LOG_PATH, E2NM_RERANKDRIVER_DEFAULT_CONFIG
from ......kg_model import KnowledgeGraphModel
from ......utils import ReturnInfo, Logger
from ......utils.errors import ReturnStatus
from ......utils.data_structs import NodeType
from ......db_drivers.kv_driver import KeyValueDriverConfig
from ......db_drivers.vector_driver import VectorDBInstance
from ......utils.cache_kv import CacheUtils
from ......rerankers import RerankerDriverConfig, RerankerDriver


@dataclass
class Entities2NodesMatcherConfig:
    """Конфигурация Entities2NodesMatcher-стадии MediumQA-ризонера.

    :param use_tree: _description_. Значение по умолчанию False.
    :type use_tree: str, optional
    :param reranker_driver_config: ... . Значение по умолчанию KC_RERANKDRIVER_DEFAULT_CONFIG.
    :param reranker_driver_config: RerankerDriverConfig, optional
    :param max_n: Максимальное количество вершин из графа знаний, которе может быть сопоставлено одной сущности. Значение по умолчанию 3.
    :type max_n: int, optional
    :param cache_table_name: Название таблицы в структуре (базе) данных, куда будут сохраняться (кешироваться) основные результаты работы Entities2NodesMatcher-класса. Значение по умолчанию 'medreasn_e2nmatcher_main_stage_cache'.
    :type cache_table_name: str, optional
    :param log: Отладочный класс для журналирования/мониторинга поведения инициализируемой комопненты. Значение по умолчанию Logger(E2NMATCHER_MAIN_LOG_PATH).
    :type log: Logger, optional
    :param verbose: Если True, то информация о поведении класса будет сохраняться в stdout и файл-журналирования (log), иначе только в файл. Значение по умолчанию False.
    :type verbose: bool, optional
    """
    use_tree: bool = False
    reranker_driver_config: RerankerDriverConfig = field(default_factory=lambda: E2NM_RERANKDRIVER_DEFAULT_CONFIG)
    max_n: int = 3

    cache_table_name: str = "medreasn_e2nmatcher_main_stage_cache"
    log: Logger = field(
        default_factory=lambda: Logger(E2NMATCHER_MAIN_LOG_PATH))
    verbose: bool = False

    def to_str(self):
        return f"{self.use_tree}|{self.max_n}|{self.reranker_driver_config.to_str()}"


class Entities2NodesMatcher(CacheUtils):
    """Верхнеуровневый класс стадии #2.1.2 medium QA-конвейера для выполнения сопоставоения сущностей из user-вопроса с вершинами в графе знаний.

    :param kg_model: Модель памяти (графа знаний) ассистента.
    :type kg_model: KnowledgeGraphModel
    :param config: Конфигурация Entities2NodesMatcher-стадии. Значение по умолчанию Entities2NodesMatcherConfig().
    :type config: Entities2NodesMatcherConfig, optional
    :param cache_kvdriver_config: Конфигурация структуры данных для кеширования промежуточных результатов в рамках компонент данного класса. Значение по умолчению None.
    :type cache_kvdriver_config: Union[KeyValueDriverConfig, None], optional
    """

    def __init__(self, kg_model: KnowledgeGraphModel, config: Entities2NodesMatcherConfig = Entities2NodesMatcherConfig(),
                 cache_kvdriver_config: Union[None, KeyValueDriverConfig] = None):
        self.config = config
        self.kg_model = kg_model

        self.cachekv = self.init_cachekv(
            cache_kvdriver_config, config.cache_table_name)

        self.retriever = RerankerDriver.specify(
            self.config.reranker_driver_config,
            kg_model.graph_embeddings.nodes_vectordbs[NodeType.object])

        self.log = self.config.log
        self.verbose = self.config.verbose

    def get_agent_tgen_stat(self) -> Union[None, Dict[str, Union[None, Dict]]]:
        return None

    def get_cache_stat(self) -> Dict[str, Union[None, Dict]]:
        return {
            'EntitiesExtractor': None if self.cachekv is None else self.cachekv.kv_conn.count_items()
        }

    def clear_kv_caches(self, level: str = 'all') -> None:
        if not isinstance(level, str):
            raise TypeError(
                f"Аргумент переменной 'level' должен иметь тип 'str'; сейчас аргумент имеет тип '{type(level)}'")
        if level not in ['all', 'current', 'other']:
            raise ValueError(
                f"Аргумент переменной 'level' должен принимать одно из трёх значенией: 'all', 'current' или 'other'. Полученное значение: '{level}'")

        if level in ['current', 'all']:
            self.cachekv.clear()

        if level in ['other']:
            raise NotImplementedError

    def get_cache_key(self, entitie: str) -> List[object]:
        return [entitie, self.config.to_str()]

    @CacheUtils.cache_method_output
    def match_entitie2knowledge(self, entitie: str) -> List[VectorDBInstance]:
        if self.config.use_tree:
            matched_objects = self.kg_model.nodestree_model.match_entitie2objects(entitie, max_n=self.config.max_n)
        else:
            matched_objects = self.retriever.run(entitie, top_k=self.config.max_n, includes=['documents'])

        return matched_objects

    def perform(self, entities: List[str]) -> Tuple[Dict[str, List[VectorDBInstance]], ReturnInfo]:
        """Метод предназначен для сопоставления заданных сущностей (на естественном языке) с вершинами из графа знаний.

        :param entities: Список сущностей.
        :type entities: List[str]
        :rtype: Tuple[Dict[str,List[VectorDBInstance]], ReturnInfo]
        """
        self.log("START ENTITIES2NODES MATCHING...",
                 verbose=self.config.verbose)
        self.log(f"ENTIITES: {entities}", verbose=self.config.verbose)
        if len(entities) < 1:
            raise ValueError
        rinfo = ReturnInfo()

        matched_kg_objects: Dict[str, List[VectorDBInstance]] = dict()
        for i, entitie in enumerate(entities):
            self.log(f"Текушая сушность #{i}: {entitie}", verbose=self.verbose)
            matched_kg_objects[entitie] = self.match_entitie2knowledge(entitie)
            str_matchedobjects = ', '.join(
                list(map(lambda obj: obj.document, matched_kg_objects[entitie])))
            self.log(f"RESULT: {str_matchedobjects}", verbose=self.verbose)

        m_objects_amount = sum(
            list(map(lambda m_objects: len(m_objects), matched_kg_objects.values())))
        if m_objects_amount < 1:
            rinfo.status = ReturnStatus.empty_answer
        self.log(f"STATUS: {rinfo.status}", verbose=self.verbose)

        return matched_kg_objects, rinfo
