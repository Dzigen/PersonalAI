from dataclasses import dataclass, field
from typing import Tuple, List, Dict, Union

from .config import E2NMATCHER_MAIN_LOG_PATH
from ......kg_model import KnowledgeGraphModel
from ......utils import ReturnInfo, Logger
from ......utils.errors import ReturnStatus
from ......utils.data_structs import NodeType
from ......db_drivers.kv_driver import KeyValueDriverConfig
from ......db_drivers.vector_driver import VectorDBInstance
from ......utils.cache_kv import CacheUtils


@dataclass
class Entities2NodesMatcherConfig:
    """Конфигурация Entities2NodesMatcher-стадии MediumQA-ризонера.

    :param use_tree: _description_. Значение по умолчанию False.
    :type use_tree: str, optional
    :param distance_threshold: Пороговое значение семантического расстояния [distance] между сущностью и вершинами в графе, по которому выполняется отсечение нерелевантных объектов (вершин). Значение по умолчанию 0.4.
    :type distance_threshold: float, optional
    :param max_n: Максимальное количество вершин из графа знаний, которе может быть сопоставлено одной сущности. Значение по умолчанию 3.
    :type max_n: int, optional
    :param fetch_k: Служебный гиперпараметр. Значение по умолчанию 50.
    :type fetch_k: int, optional
    :param cache_table_name: Название таблицы в структуре (базе) данных, куда будут сохраняться (кешироваться) основные результаты работы Entities2NodesMatcher-класса. Значение по умолчанию 'medreasn_e2nmatcher_main_stage_cache'.
    :type cache_table_name: str, optional
    :param log: Отладочный класс для журналирования/мониторинга поведения инициализируемой комопненты. Значение по умолчанию Logger(E2NMATCHER_MAIN_LOG_PATH).
    :type log: Logger, optional
    :param verbose: Если True, то информация о поведении класса будет сохраняться в stdout и файл-журналирования (log), иначе только в файл. Значение по умолчанию False.
    :type verbose: bool, optional
    """
    use_tree: bool = False
    distance_threshold: float = 0.4
    max_n: int = 3
    fetch_k: int = 50

    cache_table_name: str = "medreasn_e2nmatcher_main_stage_cache"
    log: Logger = field(
        default_factory=lambda: Logger(E2NMATCHER_MAIN_LOG_PATH))
    verbose: bool = False

    def to_str(self):
        return f"{self.use_tree}|{self.distance_threshold}|{self.max_n}|{self.fetch_k}"


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

        self.log = self.config.log
        self.verbose = self.config.verbose

    def clear_kv_caches(self, level: str = 'all') -> None:
        if type(level) is not str:
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
            matched_objects = self.kg_model.nodestree_struct.match_entitie2objects(
                entitie, distance_threshold=self.config.distance_threshold, fetch_k=self.config.fetch_k,
                max_n=self.config.max_n)
        else:
            entitie_embedding = self.kg_model.embeddings_struct.embedder.encode_queries([
                                                                                        entitie])[0]
            entitie_vinstance = VectorDBInstance(embedding=entitie_embedding)

            raw_scored_nodes = self.kg_model.embeddings_struct.vectordbs['nodes'].retrieve(
                query_instances=[entitie_vinstance], n_results=self.config.fetch_k, includes=['documents'])[0]
            filtered_nodes = list(filter(
                lambda pair: pair[0] <= self.config.distance_threshold, raw_scored_nodes))

            object_nodes = list(filter(lambda pair: self.kg_model.graph_struct.db_conn.get_node_type(
                pair[1].id) == NodeType.object, filtered_nodes))
            matched_objects = list(map(lambda pair: pair[1], sorted(
                object_nodes, key=lambda p: p[0], reverse=False)))[:self.config.max_n]

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

        matched_kg_objects = dict()
        for i, entitie in enumerate(entities):
            self.log(f"Текушая сушность #{i}: {entitie}", verbose=self.verbose)
            matched_kg_objects[entitie] = self.match_entitie2knowledge(entitie, use_tree=self.config.use_tree,
                                                                       distance_threshold=self.config.distance_threshold,
                                                                       max_n=self.config.max_n, fetch_k=self.config.fetch_k)
            str_matchedobjects = ', '.join(
                list(map(lambda obj: obj.document, matched_kg_objects[entitie])))
            self.log(f"RESULT: {str_matchedobjects}", verbose=self.verbose)

        m_objects_amount = sum(
            list(map(lambda m_objects: len(m_objects), matched_kg_objects.values())))
        if m_objects_amount < 1:
            rinfo.status = ReturnStatus.empty_answer
        self.log(f"STATUS: {rinfo.status}", verbose=self.verbose)

        return matched_kg_objects, rinfo
