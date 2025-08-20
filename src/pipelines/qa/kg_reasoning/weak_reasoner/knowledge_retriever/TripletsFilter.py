from dataclasses import dataclass
from typing import List, Union, Dict
import hashlib

from .utils import AbstractTriplesFilter, BaseTripletsFilterConfig
from ......utils.data_structs import Triplet, QueryInfo, create_id, TripletCreator
from ......utils import Logger
from ......kg_model import KnowledgeGraphModel
from ......db_drivers.vector_driver import VectorDBInstance
from ......utils.cache_kv import CacheUtils
from ......db_drivers.kv_driver import KeyValueDriverConfig


@dataclass
class TripletsFilterConfig(BaseTripletsFilterConfig):
    """Конфигурация наивного алгоритма ранжирования/фильтрации триплетов.

    :param max_k: Первые k (по релевантности) триплетов, которые будут возвращены в результате операции ранжирования. Значение по умолчанию 50.
    :type max_k: int
    :param cache_table_name: Название таблицы в структуре (базе) данных, куда будут сохраняться (кешироваться) основные результаты работы TripletsFilter-класса. Значение по умолчанию 'qa_naive_t_filter_cache'.
    :type cache_table_name: str
    """
    max_k: int = 50
    cache_table_name: str = 'qa_naive_t_filter_cache'

    def to_str(self):
        return f"{self.max_k}"


class TripletsFilter(AbstractTriplesFilter, CacheUtils):
    """Класс реализует логику наивного ранжирования/фильтрации триплетов на основе их релевантности к user-вопросу.

    :param kg_model: Модель памяти (графа знаний) ассистента.
    :type kg_model: KnowledgeGraphModel
    :param log: Отладочный класс для журналирования/мониторинга поведения инициализируемой компоненты.
    :type log: Logger
    :param config: Конфигурация наивного алгоритма фильтрации. Значение по умолчанию TripletsFilterConfig().
    :type config: Union[TripletsFilterConfig, Dict], optional
    :param cache_kvdriver_config: Конфигурация структуры данных для кеширования промежуточных результатов в рамках компонент данного класса. Значение по умолчению None.
    :type cache_kvdriver_config: Union[KeyValueDriverConfig, None], optional
    :param verbose: Если True, то информация о поведении класса будет сохраняться в stdout и файл-журналирования (log), иначе только в файл. Значение по умолчанию False.
    :type verbose: bool, optional
    """
    def __init__(self, kg_model: KnowledgeGraphModel, log: Logger, config: Union[TripletsFilterConfig, Dict] = TripletsFilterConfig(),
                 cache_kvdriver_config: Union[None,KeyValueDriverConfig] = None, verbose: bool = False) -> None:
        if type(config) is dict:
            config = TripletsFilterConfig(**config)
        self.config = config
        self.kg_model = kg_model

        self.cachekv = self.init_cachekv(cache_kvdriver_config, config.cache_table_name)

        self.log = log
        self.verbose = verbose

    def clear_kv_caches(self, level = 'all') -> None:
        if type(level) is not str:
            raise TypeError(f"Аргумент переменной 'level' должен иметь тип 'str'; сейчас аргумент имеет тип '{type(level)}'")
        if level not in ['all', 'current', 'other']:
            raise ValueError(f"Аргумент переменной 'level' должен принимать одно из трёх значенией: 'all', 'current' или 'other'. Полученное значение: '{level}'")

        if level in ['current', 'all']:
            self.cachekv.clear()

        if level == 'other':
            raise NotImplementedError


    def get_cache_key(self, query_info: QueryInfo, triplets: List[Triplet]) -> List[str]:
        str_triplets = hashlib.sha1("\n".join(sorted([TripletCreator.stringify(triplet)[1] for triplet in triplets])).encode()).hexdigest()
        return [self.config.to_str(), query_info.to_str(), str_triplets]

    @CacheUtils.cache_method_output
    def apply_filter(self, query_info: QueryInfo, triplets: List[Triplet]) -> List[Triplet]:
        self.log("START KNOWLEDGE FILTERING...", verbose=self.verbose)
        self.log("FILTER: NaiveTripletFilter", verbose=self.verbose)
        self.log(f"BASE_QUESTION ID: {create_id(query_info.query)}", verbose=self.verbose)
        self.log(f"BASE_QUESTION: {query_info.query}", verbose=self.verbose)

        unique_relations_map = {triplet.relation.id: triplet for triplet in triplets}
        filtered_triplets = []

        self.log(f"Всего триплетов: {len(triplets)}", verbose=self.verbose)
        self.log(f"Количество уникальных триплетов (по строковому представлению): {len(set(unique_relations_map))}", verbose=self.verbose)
        self.log(f"base ids: {list(unique_relations_map.keys())}", verbose=self.verbose)

        if len(unique_relations_map) <= self.config.max_k:
            filtered_triplets = list(unique_relations_map.values())
        else:
            query_embd = self.kg_model.embeddings_struct.embedder.encode_queries([query_info.query])[0]
            query_instance = VectorDBInstance(embedding=query_embd)

            relation_ids = list(unique_relations_map.keys())

            raw_relevant_triplets = self.kg_model.embeddings_struct.vectordbs['triplets'].retrieve(
                [query_instance], self.config.max_k, subset_ids=relation_ids)[0]

            accepted_relation_ids = list(map(lambda item: item[1].id, raw_relevant_triplets))

            self.log(f"Количество accepted ids: {len(accepted_relation_ids)}", verbose=self.verbose)
            self.log(f"Количество уникальных accepted ids: {len(set(accepted_relation_ids))}", verbose=self.verbose)
            self.log(f"accepted ids: {accepted_relation_ids}", verbose=self.verbose)

            filtered_triplets = list(map(lambda rel_id: unique_relations_map[rel_id], accepted_relation_ids))

        self.log(f"Количество триплето после фильтрации: {len(filtered_triplets)}", verbose=self.verbose)

        return filtered_triplets
