from typing import List

from .graph_model import GraphModelConfig, GraphModel
from .embeddings_model import EmbeddingsModelConfig, EmbeddingsModel
from ..utils import Triplet

class KnowledgeGraphModel:
    """Модель памяти (графа знаний) ассистента.

    :param graph_struct: Знания, хранящиеся в графовой структуре данных.
    :type graph_struct: GraphModel
    :param graph_struct: Знания, хранящиеся в векторной структуре данных.
    :type graph_struct: EmbeddingsModel
    """

    def __init__(self, graph_config: GraphModelConfig, embeddings_config: EmbeddingsModelConfig) -> None:
        self.graph_struct = GraphModel(graph_config)
        self.embeddings_struct =  EmbeddingsModel(embeddings_config)

    def add_knowledge(self, triplets: List[Triplet], update_nodes: bool = False) -> None:
        # на уровне графа знаний выдерживается консистентность графовой и векторой моделей
        self.graph_struct.create_triplets(triplets, status_bar=False) # внутри идёт сначала create , а потом update
        self.embeddings_struct.create_triplets(triplets, status_bar=False)

    def remove_knowledge(self, triplet_ids: List[str]) -> None:
        self.graph_struct.delete_triplets(triplet_ids)
        self.embeddings_struct.delete_triplets(triplet_ids, delete_nodes=True)

    def clear(self) -> None:
        self.embeddings_struct.clear()
        self.graph_struct.clear()
