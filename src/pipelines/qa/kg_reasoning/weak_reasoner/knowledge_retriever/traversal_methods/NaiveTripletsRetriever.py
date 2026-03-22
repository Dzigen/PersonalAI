from typing import List, Dict, Union, Tuple
from dataclasses import dataclass, field
from collections import Counter
from copy import deepcopy

from .configs import NGS_RERANKDRIVER_DEFAULT_CONFIG, NAIVE_RETRIEVER_LOG_PATH
from ..utils import AbstractTripletsRetriever, BaseGraphSearchConfig
from .......db_drivers.vector_driver import VectorDBInstance
from .......kg_model import KnowledgeGraphModel
from .......utils import Logger, accumulate_step_info, ReturnInfo
from .......utils.data_structs import QueryInfo, Triplet, create_id
from .......utils.cache_kv import CacheUtils
from .......db_drivers.kv_driver import KeyValueDriverConfig
from .......rerankers import RerankerDriver, RerankerDriverConfig


@dataclass
class NaiveGraphSearchConfig(BaseGraphSearchConfig):
    """Конфигурация NaiveRetrieval-алгоритма обхода графа.

    :param reranker_driver_config: Конфигурация Retrieve/Rerank-оператора. Значение по умолчанию NGS_RERANKDRIVER_DEFAULT_CONFIG.
    :type reranker_driver_config: Union[Dict, RerankerDriverConfig], optional
    :param max_k: Максимальное количество триплетов, которое может быть извлечено из графа. Значение по умолчанию 50.
    :type max_k: int, optional
    :param cache_table_name: Название таблицы в структуре (базе) данных, куда будут сохраняться (кешироваться) основные результаты работы NaiveTripletsRetriever-класса. Значение по умолчанию 'qa_naive_t_retriever_cache'.
    :type cache_table_name: str, optional
    """
    reranker_driver_config: Union[Dict, RerankerDriverConfig] = field(default_factory=lambda: NGS_RERANKDRIVER_DEFAULT_CONFIG)
    max_k: int = 50

    cache_table_name: str = 'qa_naive_t_retriever_cache'
    log_path: str = NAIVE_RETRIEVER_LOG_PATH

    def to_str(self):
        return f"{self.max_k};{self.reranker_driver_config.to_str()}"

    @staticmethod
    def from_dict(dict_config: Dict):
        dictconfig_copy = deepcopy(dict_config)
        formated_config = NaiveGraphSearchConfig(**dictconfig_copy)
        formated_config.formate_fields()
        return formated_config

    def formate_fields(self) -> None:
        if isinstance(self.reranker_driver_config, dict):
            self.reranker_driver_config = RerankerDriverConfig.from_dict(self.reranker_driver_config)
        else:
            self.reranker_driver_config.formate_fields()


class NaiveTripletsRetriever(AbstractTripletsRetriever, CacheUtils):
    """Класс предназначен для извлечения триплетов из графа знаний на основе оценки семантической близости триплетов к запросу (стандартный retrieval).

    :param kg_model: Модель памяти (графа знаний) ассистента.
    :type kg_model: KnowledgeGraphModel
    :param search_config: Конфигурация WaterCirclesRetriever-алгоритма. Значение по умолчанию  NaiveGraphSearchConfig().
    :type search_config: Union[NaiveGraphSearchConfig,Dict], optional
    :param cache_kvdriver_config: Конфигурация структуры данных для кеширования промежуточных результатов в рамках компонент данного класса. Значение по умолчанию None.
    :type cache_kvdriver_config: Union[None, KeyValueDriverConfig], optional
    """

    def __init__(self, kg_model: KnowledgeGraphModel, search_config: Union[NaiveGraphSearchConfig, Dict] = NaiveGraphSearchConfig(),
                 cache_kvdriver_config: Union[None, KeyValueDriverConfig] = None) -> None:
        if isinstance(search_config, dict):
            search_config = NaiveGraphSearchConfig.from_dict(search_config)
        else:
            search_config.formate_fields()
        self.config: NaiveGraphSearchConfig = search_config

        self.kg_model = kg_model

        self.cachekv = self.init_cachekv(
            cache_kvdriver_config, self.config.cache_table_name)

        self.retriever = RerankerDriver.specify(
            self.config.reranker_driver_config,
            kg_model.graph_embeddings.triplets_vcomposer
        )

        self.log = Logger(search_config.log_path)
        self.verbose = search_config.verbose
        self.log_level = search_config.log_level

    def close_connections(self):
        if self.cachekv is not None:
            self.cachekv.close_connection()

    def get_traversal_cache(self) -> None:
        return None

    def clear_traversal_cache(self) -> None:
        pass

    def get_cache_key(self, query_info: QueryInfo) -> List[object]:
        return [self.config.to_str(), query_info.to_str()]

    @accumulate_step_info
    @CacheUtils.cache_method_output
    def get_relevant_triplets(self, query_info: QueryInfo) -> Tuple[List[Triplet], ReturnInfo]:
        self.log.debug("START KNOWLEDGE RETRIEVING ...", verbose=self.verbose, log_level=self.log_level)
        self.log.debug("* Retriever: NaiveTripletsRetriever", verbose=self.verbose, log_level=self.log_level)
        self.log.debug("* Question hash: %s", create_id(query_info.query), verbose=self.verbose, log_level=self.log_level)
        self.log.debug("* Question: %s", query_info.query, verbose=self.verbose, log_level=self.log_level)
        rinfo = ReturnInfo()

        relevant_triplets: List[VectorDBInstance] = self.retriever.run(query_info.query, top_k=self.config.max_k)
        triplet_ids = list(map(lambda item: item.metadata['t_id'], relevant_triplets))
        self.log.debug("Количество извлечённых объектов из векторной бд (triplets): %d", len(triplet_ids), verbose=self.verbose, log_level=self.log_level)

        triplets: List[Triplet] = self.kg_model.graph_struct.db_conn.read(triplet_ids)
        self.log.debug("Количество полученных трипелтов из графовой бд: %d", len(triplets), verbose=self.verbose, log_level=self.log_level)
        self.log.debug("Распределение типов связей в наборе извлечённых триплетов: %s",
                       Counter([triplet.relation.type for triplet in triplets]), verbose=self.verbose, log_level=self.log_level)

        return triplets, rinfo
