from dataclasses import dataclass
from typing import List

from .utils import AbstractTriplesFilter, BaseTripletsFilterConfig
from ....utils.data_structs import Triplet, QueryInfo, create_id
from ....utils import Logger
from ....kg_model import KnowledgeGraphModel
from ....db_drivers.vector_driver import VectorDBInstance

@dataclass
class TripletsFilterConfig(BaseTripletsFilterConfig):
    """Конфигурация наивного алгоритма ранжирования/фильтрации триплетов.

    :param max_k: Первые k (по релевантности) триплетов, которые будут возвращены в результате операции ранжирования. Значение по умолчанию 50.
    :type max_k: int
    """
    max_k: int = 50

class TripletsFilter(AbstractTriplesFilter):
    """Класс реализует логику наивного ранжирования/фильтрации триплетов на основе их релевантности к user-вопросу.

    :param kg_model: Модель памяти (графа знаний) ассистента.
    :type kg_model: KnowledgeGraphModel
    :param config: Конфигурация наивного алгоритма фильтрации. Значение по умолчанию TripletsFilterConfig().
    :type config: TripletsFilterConfig
    :param log: Отладочный класс для журналирования/мониторинга поведения инициализируемой компоненты. Значение по умолчанию Logger(LOG_PATH).
    :type log: Logger
    :param verbose: Если True, то информация о поведении класса будет сохраняться в stdout и файл-журналирования (log), иначе только в файл. Значение по умолчанию False.
    :type verbose: bool
    """
    def __init__(self, kg_model: KnowledgeGraphModel, log: Logger, config: TripletsFilterConfig = TripletsFilterConfig(), verbose: bool = False) -> None:
        self.log = log
        self.verbose = verbose
        self.kg_model = kg_model
        self.config = config

    def apply_filter(self, query_info: QueryInfo, triplets: List[Triplet]) -> List[Triplet]:
        self.log("START KNOWLEDGE FILTERING...", verbose=self.verbose)
        self.log(f"BASE_QUESTION ID: {create_id(query_info.query)}", verbose=self.verbose)
        self.log(f"BASE_QUESTION: {query_info.query}", verbose=self.verbose)

        filtered_triplets = []
        query_embd = self.kg_model.embeddings_struct.embedder.encode_queries([query_info.query])[0]
        query_instance = VectorDBInstance(embedding=query_embd)
        base_relation_ids = list(map(lambda triplet: triplet.relation.id, triplets))

        self.log(f"Всего триплетов: {len(base_relation_ids)}", verbose=self.verbose)
        self.log(f"Количество уникальных триплетов: {len(set(base_relation_ids))}", verbose=self.verbose)
        self.log(f"base ids: {base_relation_ids}", verbose=self.verbose)

        if len(base_relation_ids) > 0:
            raw_relevant_triplets = self.kg_model.embeddings_struct.vectordbs['triplets'].retrieve(
                [query_instance], self.config.max_k, includes=['embeddings', 'documents', 'metadatas'], where={"id": {"$in": base_relation_ids}})[0]

            accepted_tripletes_ids = list(map(lambda item: item[1].id, raw_relevant_triplets))
            self.log(f"Количество accepted ids: {len(accepted_tripletes_ids)}", verbose=self.verbose)
            self.log(f"Количество уникальных accepted ids: {len(set(accepted_tripletes_ids))}", verbose=self.verbose)
            self.log(f"accepted ids: {accepted_tripletes_ids}", verbose=self.verbose)

            filtered_triplets = list(filter(lambda triplet: triplet.relation.id in accepted_tripletes_ids, triplets))
            self.log(f"Количество filtered triplets: {len(filtered_triplets)}", verbose=self.verbose)

        return filtered_triplets
