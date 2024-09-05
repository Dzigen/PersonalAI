from .utils import KnowledgeComparatorConfig
from ..query_parser.utils import ParsedQueryStructure
from ...knowledge_graph_model import KnowledgeGraphModel
from ...embedding_functions import VectorDBInstance

class KnowledgeComparator:
    def __init__(self, config: KnowledgeComparatorConfig, kg_model: KnowledgeGraphModel) -> None:
        self.config = config
        self.kg_model = kg_model

        self.kg_model.embeddings_db.embedder.encode_queries()

    def link_kgnodes_to_query(self, query_structure: ParsedQueryStructure):
        # сопостовляем сущности, извлечённые из запроса нодам в графе знаний
        linked_nodess = []
        for entity in query_structure.entities:
            entity_embedding = self.kg_model.embeddings_db.embedder.encode_query(entity)
            entity_instance = VectorDBInstance(embedding=entity_embedding)

            nodes_with_scores = self.kg_model.embeddings_db.vecordbs['nodes'].retrieve(entity_instance, n_results=self.config.fetch_n)
            filtered_nodes = list(filter(lambda node_item: node_item[0] < self.config.threshold, nodes_with_scores))
                
            if self.config.max_k > 0:
                filtered_nodes = filtered_nodes[:self.config.max_k]

            linked_nodess += list(map(lambda node_item: node_item[1], filtered_nodes))

        unique_nodes_ids = []
        unique_nodes = []
        for node in linked_nodess:
            if node.id not in unique_nodes_ids:
                unique_nodes_ids.append(node.id)
                unique_nodes.append(node)

        return linked_nodess
