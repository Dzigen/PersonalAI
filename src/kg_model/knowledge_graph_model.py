from typing import List

from .graph_model import GraphModel
from .embeddings_model import EmbeddingsModel
from ..utils import Triplet

class KnowledgeGraphModel:
    """Модель памяти (графа знаний) ассистента.

    :param graph_struct: Знания, хранящиеся в графовой структуре данных.
    :type graph_struct: GraphModel
    :param graph_struct: Знания, хранящиеся в векторной структуре данных.
    :type graph_struct: EmbeddingsModel
    """

    def __init__(self, graph_struct: GraphModel, embeddings_model: EmbeddingsModel) -> None:
        self.graph_struct = graph_struct
        self.embeddings_struct =  embeddings_model

    def create_triplets(self, triplets: List[Triplet], update_nodes: bool = False) -> None:
        # на уровне графа знаний выдерживается консистентность графовой и векторой моделей
        self.graph_struct.create_triplets(triplets, status_bar=False) # внутри идёт сначала create , а потом update
        self.embeddings_struct.create_triplets(triplets, status_bar=False)

    def delete_triplets(self):
        # TODO
        pass

    def update_relations(self):
        # TODO
        pass

    def update_nodes(self):
        # TODO
        pass
