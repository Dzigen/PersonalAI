from typing import List, Dict, Set

from .graph_model import GraphModelConfig, GraphModel
from .embeddings_model import EmbeddingsModelConfig, EmbeddingsModel
from ..utils import Triplet, Logger

KG_MAIN_LOG_PATH = 'log/kg_model/main'

class KnowledgeGraphModel:
    """Модель памяти (графа знаний) ассистента.

    :param graph_config: Конфигурация модели, которая будет использоваться для хранения информации в графовой структуре данных.
    :type graph_struct: GraphModel
    :param embeddings_config: Конфигурация модели, которая будет использоваться для хранения информации в векторной структуре данных.
    :type embeddings_config: EmbeddingsModel
    """

    def __init__(self, graph_config: GraphModelConfig = GraphModelConfig(), embeddings_config: EmbeddingsModelConfig = EmbeddingsModelConfig(), verbose: bool = False) -> None:
        self.graph_struct = GraphModel(graph_config)
        self.embeddings_struct =  EmbeddingsModel(embeddings_config)

        self.log = Logger(KG_MAIN_LOG_PATH)
        self.verbose = verbose

    def check_consistency(self) -> None:
        gdb_count = self.graph_struct.db_conn.count_items()
        self.log(f"GRAPH DB STATUS: {gdb_count}", verbose=self.verbose)
        vdb_nodes_count = self.embeddings_struct.vectordbs['nodes'].count_items()
        vdb_triplets_count = self.embeddings_struct.vectordbs['triplets'].count_items()
        self.log(f"VECTOR DB STATUS: {vdb_nodes_count} - nodes; {vdb_triplets_count} - triplets", verbose=self.verbose)

        assert gdb_count['nodes'] == vdb_nodes_count
        assert gdb_count['triplets'] >= vdb_triplets_count
        #assert vdb_nodes_count > vdb_triplets_count

    def add_knowledge(self, triplets: List[Triplet], check_consistency: bool = True) -> Dict[str, Dict[str,Set[str]]]:
        """Метод предназначен для добавления информации в память (граф знаний) асситента в виде формате списка триплетов.

        :param triplets: Список триплетов с информацией для добавления в память (граф знаний) асситента.
        :type triplets: List[Triplet]
        """

        graph_create_info = self.graph_struct.create_triplets(triplets, status_bar=False)
        embd_create_info = self.embeddings_struct.create_triplets(triplets, status_bar=False)

        if check_consistency:
            self.check_consistency()

        return {'graph_info': graph_create_info, 'embeddings_info': embd_create_info}

    def remove_knowledge(self, triplets: List[Triplet], check_consistency: bool = True) -> Dict[str, Dict[int,Dict[str,bool]]]:
        """Метод предназанчен для удаления информации из памяти (графа знаний) асситента.
        Удаление производится по идентификаторам триплетов, в которых данная информация находилась
        при её добавлении в память с помощью соответствующего add_knowledge-метода.

        :param triplets: Набор триплетов, по которым нужно удалить соответствующую информацию из памяти ассистента.
        :type triplet_ids: List[str]
        """
        graph_delete_info, embds_delete_info = self.graph_struct.delete_triplets(triplets)
        self.embeddings_struct.delete_triplets(triplets, delete_info=embds_delete_info)

        if check_consistency:
            self.check_consistency()

        return {'graph_info': graph_delete_info, 'embeddings_info': embds_delete_info}

    def count_items(self) -> Dict[str, Dict[str, int]]:
        return {
            'graph_info': self.graph_struct.count_items(),
            'embeddings_info': self.embeddings_struct.count_items()
        }

    def clear(self) -> None:
        """Метод предназначен для удаления содержимого памяти (графа знаний) ассистента.
        """
        self.embeddings_struct.clear()
        self.graph_struct.clear()
