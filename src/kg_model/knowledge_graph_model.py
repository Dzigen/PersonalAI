from typing import List

from .graph_model import GraphModelConfig, GraphModel
from .embeddings_model import EmbeddingsModelConfig, EmbeddingsModel
from ..utils import Triplet

class KnowledgeGraphModel:
    """Модель памяти (графа знаний) ассистента.

    :param graph_config: Конфигурация модели, которая будет использоваться для хранения информации в графовой структуре данных.
    :type graph_struct: GraphModel
    :param embeddings_config: Конфигурация модели, которая будет использоваться для хранения информации в векторной структуре данных.
    :type embeddings_config: EmbeddingsModel
    """

    def __init__(self, graph_config: GraphModelConfig, embeddings_config: EmbeddingsModelConfig) -> None:
        self.graph_struct = GraphModel(graph_config)
        self.embeddings_struct =  EmbeddingsModel(embeddings_config)

    def add_knowledge(self, triplets: List[Triplet]) -> None:
        """Метод предназначен для добавления информации в память (граф знаний) асситента в виде формате списка триплетов.

        :param triplets: Список триплетов с информацией для добавления в память (граф знаний) асситента.
        :type triplets: List[Triplet]
        """

        self.graph_struct.create_triplets(triplets, status_bar=False)
        self.embeddings_struct.create_triplets(triplets, status_bar=False)

    def remove_knowledge(self, triplet_ids: List[str]) -> None:
        """Метод предназанчен для удаления информации из памяти (графа знаний) асситента.
        Удаление производится по идентификаторам триплетов, в которых данная информация находилась
        при её добавлении в память с помощью соответствующего add_knowledge-метода.

        :param triplet_ids: Идентификаторы триплетов, по которым нужно удалить соответствующую инфомрацию из памяти ассистента.
        :type triplet_ids: List[str]
        """
        self.graph_struct.delete_triplets(triplet_ids)
        self.embeddings_struct.delete_triplets(triplet_ids, delete_nodes=True)

    def clear(self) -> None:
        """Метод предназначен для удаления содержимого памяти (графа знаний) ассистента.
        """
        self.embeddings_struct.clear()
        self.graph_struct.clear()
