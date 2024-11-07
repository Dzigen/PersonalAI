from dataclasses import dataclass, field

from .utils import COMPARATOR_LOG_PATH
from ...utils import Logger, ReturnStatus, ReturnInfo
from ...utils.errors import QA_ZERO_LINKED_NODES_MSG
from ...utils.data_structs import QueryInfo
from ...knowledge_graph_model import KnowledgeGraphModel
from ...db_drivers.vector_driver import VectorDBInstance

@dataclass
class KnowledgeComparatorConfig:
    """_summary_
    """
    #
    threshold: float = 0.5
    #
    fetch_n: int = 20
    #
    max_k: int = 1
    #
    k_compare: int = 5
    #
    log: Logger = field(default_factory=lambda: Logger(COMPARATOR_LOG_PATH))
    log_verbose: bool = False

class KnowledgeComparator:
    """Главный класс для сопостовения информации в пользовательском запросе
    с имеющейся информацией в графе знаний
    """
    def __init__(self, kg_model: KnowledgeGraphModel, config: KnowledgeComparatorConfig = KnowledgeComparatorConfig()) -> None:
        """_summary_

        :param kg_model: _description_
        :type kg_model: KnowledgeGraphModel
        :param config: _description_, defaults to KnowledgeComparatorConfig()
        :type config: KnowledgeComparatorConfig, optional
        """
        self.config = config
        self.kg_model = kg_model

    def link_kgnodes_to_query(self, query_structure: QueryInfo) -> ReturnInfo:
        """_summary_

        :param query_structure: _description_
        :type query_structure: QueryInfo
        :return: _description_
        :rtype: ReturnInfo
        """
        # сопоставляем сущности, извлечённые из запроса нодам в графе знаний
        info = ReturnInfo()
        linked_nodes_by_entities, linked_nodes = [], []
        for entity in query_structure.entities:
            entity_embedding = self.kg_model.embeddings_struct.embedder.encode_queries([entity])[0]
            entity_instance = VectorDBInstance(embedding=entity_embedding)

            nodes_with_scores = self.kg_model.embeddings_struct.vectordbs['nodes'].retrieve(
                [entity_instance], n_results=self.config.fetch_n)[0]
            filtered_nodes = list(filter(lambda node_item: node_item[0] < self.config.threshold, nodes_with_scores))
            cur_linked_nodes = list(map(lambda node_item: node_item[1], filtered_nodes))
            linked_nodes += cur_linked_nodes[:self.config.max_k]

            cur_documents = list(map(lambda item: item.document, cur_linked_nodes))
            cur_documents_lower = list(map(lambda document: document.lower(), cur_documents))
            if entity.lower() in cur_documents_lower[:self.config.k_compare]:
                cur_unique_names = [entity]
            else:
                cur_unique_names = [entity] + cur_documents[:self.config.max_k]
            linked_nodes_by_entities.append(cur_unique_names)

        query_structure.linked_nodes = linked_nodes
        query_structure.linked_nodes_by_entities = linked_nodes_by_entities

        if len(query_structure.linked_nodes) == 0:
            info.status = ReturnStatus.zero_linked_nodes
            info.message = QA_ZERO_LINKED_NODES_MSG

        return info
