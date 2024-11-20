from .graph_model import GraphModel
from .embeddings_model import EmbeddingsModel

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

    def create_triplets(self):
        # TODO
        pass

    def delete_triplets(self):
        # TODO
        pass

    def update_relations(self):
        # TODO
        pass

    def update_nodes(self):
        # TODO
        pass
