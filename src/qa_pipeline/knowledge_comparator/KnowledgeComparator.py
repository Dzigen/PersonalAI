from ...utils.data_structs import QueryInfo
from ...knowledge_graph_model import KnowledgeGraphModel
from ...embedding_functions import VectorDBInstance

from dataclasses import dataclass

@dataclass
class KnowledgeComparatorConfig:
    threshold: float = 0.5
    fetch_n: int = 20
    max_k: int = 1

class KnowledgeComparator:
    """Главный класс для сопостовения информации в пользовательском запросе
    с имеющейся информацией в графе знаний
    """
    def __init__(self, kg_model: KnowledgeGraphModel, config: KnowledgeComparatorConfig = KnowledgeComparatorConfig()) -> None:
        self.config = config
        self.kg_model = kg_model

    def link_kgnodes_to_query(self, query_structure: QueryInfo) -> None:
        # сопоставляем сущности, извлечённые из запроса нодам в графе знаний
        
        linked_nodess = []
        entities_embeddings = self.kg_model.embeddings_db.embedder.encode_queries(query_structure.entities)
        entities_instances = list(map(lambda embed: VectorDBInstance(embedding=embed), entities_embeddings))
        nodes_with_scores = self.kg_model.embeddings_db.vectordbs['nodes'].retrieve(entities_instances, n_results=self.config.fetch_n)

        for retrieved_instances in nodes_with_scores:    
            filtered_nodes = list(filter(lambda node_item: node_item[0] < self.config.threshold, retrieved_instances))
                
            if self.config.max_k > 0:
                filtered_nodes = filtered_nodes[:self.config.max_k]
            linked_nodess += list(map(lambda node_item: node_item[1], filtered_nodes))

        unique_nodes_ids = []
        unique_nodes = []
        for node in linked_nodess:
            if node.id not in unique_nodes_ids:
                unique_nodes_ids.append(node.id)
                unique_nodes.append(node)

        query_structure.linked_nodes = unique_nodes

