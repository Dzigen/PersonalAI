from typing import List, Dict, Union
from dataclasses import dataclass, field
from collections import Counter

from .configs import NGS_RERANKDRIVER_DEFAULT_CONFIG
from ..utils import AbstractTripletsRetriever, BaseGraphSearchConfig
from .......db_drivers.vector_driver import VectorDBInstance
from .......kg_model import KnowledgeGraphModel
from .......utils import Logger
from .......utils.data_structs import QueryInfo, Triplet, create_id
from .......utils.cache_kv import CacheUtils
from .......db_drivers.kv_driver import KeyValueDriverConfig
from .......rerankers import RerankerDriver, RerankerDriverConfig


@dataclass
class NaiveGraphSearchConfig(BaseGraphSearchConfig):
    """Конфигурация NaiveRetrieval-алгоритма обхода графа.

    :param reranker_driver_config: ... . Значение по умолчанию GS_RERANKDRIVER_DEFAULT_CONFIG.
    :param RerankerDriverConfig, optional
    :param max_k: Макисмальное количество трипелтов, которое может быть извлечено из графа. Значение по умолчанию 50.
    :type max_k: int, optional
    :param cache_table_name: Название таблицы в структуре (базе) данных, куда будут сохраняться (кешироваться) основные результаты работы NaiveTripletsRetriever-класса. Значение по умолчанию 'qa_naive_t_retriever_cache'.
    :type cache_table_name: str, optional
    """
    reranker_driver_config: RerankerDriverConfig = field(default_factory=lambda: NGS_RERANKDRIVER_DEFAULT_CONFIG)
    max_k: int = 50
    cache_table_name: str = 'qa_naive_t_retriever_cache'

    def to_str(self):
        return f"{self.max_k}"


class NaiveTripletsRetriever(AbstractTripletsRetriever, CacheUtils):
    """Класс предназначен для извлечения триплетов из графа знаний на основе оценки семантической близости триплетов к запросу (стандартный retrieval).

    :param kg_model: Модель памяти (графа знаний) ассистента.
    :type kg_model: KnowledgeGraphModel
    :param log: Отладочный класс для журналирования/мониторинга поведения инициализируемой компоненты.
    :type log: Logger
    :param search_config: Конфигурация WaterCirclesRetriever-алгоритма. Значение по умолчанию  NaiveGraphSearchConfig().
    :type search_config: Union[NaiveGraphSearchConfig,Dict], optional
    :param cache_kvdriver_config: Конфигурация структуры данных для кеширования промежуточных результатов в рамках компонент данного класса. Значение по умолчению None.
    :type cache_kvdriver_config: Union[None,KeyValueDriverConfig], optional
    :param verbose: Если True, то информация о поведении класса будет сохраняться в stdout и файл-журналирования (log), иначе только в файл. Значение по умолчанию False.
    :type verbose: bool, optional
    """

    def __init__(self, kg_model: KnowledgeGraphModel, log: Logger, search_config: Union[NaiveGraphSearchConfig, Dict] = NaiveGraphSearchConfig(),
                 cache_kvdriver_config: Union[None, KeyValueDriverConfig] = None, verbose: bool = False) -> None:
        if isinstance(search_config, dict):
            search_config = NaiveGraphSearchConfig(**search_config)
        self.config = search_config

        self.kg_model = kg_model

        self.cachekv = self.init_cachekv(
            cache_kvdriver_config, self.config.cache_table_name)

        self.retriever = RerankerDriver.specify(
            self.config.reranker_driver_config,
            kg_model.graph_embeddings.triplets_vectordbs
        )

        self.log = log
        self.verbose = verbose

    def get_agent_tgen_stat(self) -> Union[None, Dict[str, Union[None, Dict]]]:
        return None

    def get_cache_stat(self) -> Dict[str, Union[None, Dict]]:
        return {'NaiveTripletsRetriever': None if self.cachekv is None else self.cachekv.kv_conn.count_items()}

    def clear_kv_caches(self, level='all') -> None:
        if not isinstance(level, str):
            raise TypeError(
                f"Аргумент переменной 'level' должен иметь тип 'str'; сейчас аргумент имеет тип '{type(level)}'")
        if level not in ['all', 'current', 'other']:
            raise ValueError(
                f"Аргумент переменной 'level' должен принимать одно из трёх значенией: 'all', 'current' или 'other'. Полученное значение: '{level}'")

        if level in ['current', 'all']:
            self.cachekv.clear()

        if level == 'other':
            raise NotImplementedError

    def get_cache_key(self, query_info: QueryInfo) -> List[object]:
        return [self.config.to_str(), query_info.to_str()]

    @CacheUtils.cache_method_output
    def get_relevant_triplets(self, query_info: QueryInfo) -> List[Triplet]:
        self.log("START KNOWLEDGE RETRIEVING ...", verbose=self.verbose)
        self.log("RETRIEVER: NaiveTripletsRetriever", verbose=self.verbose)
        self.log(f"BASE_QUESTION ID: {create_id(query_info.query)}", verbose=self.verbose)
        self.log(f"BASE_QUESTION: {query_info.query}", verbose=self.verbose)

        relevant_triplets: List[VectorDBInstance] = self.retriever.run(query_info.query, top_k=self.config.max_k)
        triplet_ids = list(map(lambda item: item.metadata['t_id'], relevant_triplets))
        self.log(f"Количество извлечённых объектов из векторной бд (triplets): {len(triplet_ids)}", verbose=self.verbose)

        triplets: List[Triplet] = self.kg_model.graph_struct.db_conn.read(triplet_ids)
        self.log(f"Количество полученных трипелтов из графовой бд: {len(triplets)}", verbose=self.verbose)
        self.log(f"Распределение типов связей в наборе извлечённых триплетов: {Counter([triplet.relation.type for triplet in triplets])}", verbose=self.verbose)

        return triplets
