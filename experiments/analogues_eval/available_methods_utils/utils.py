from abc import ABC, abstractmethod
from typing import Dict, List

class GraphRAGBaseOperations:

    method: object
    config: object

    def __init__(self, config: Dict) -> None:
        pass

    @abstractmethod
    @staticmethod
    def prepare_method_config(env_params: Dict, hyperp_params: Dict) -> Dict:
        pass

    @abstractmethod
    @staticmethod
    def prepare_method_env_params(self, conn_params: Dict, hyperp_params: Dict) -> List[Dict[str,str]]:
        pass

class GraphRAGBuildOperations(GraphRAGBaseOperations):
    @abstractmethod
    def build_graph(documents: List[str]) -> None:
        pass

    @abstractmethod
    def save_graph(self, env_params: Dict, hyperp_params: Dict) -> None:
        pass

    @abstractmethod
    def print_graph_info(self) -> None:
        pass

class GraphRAGQAOperations(GraphRAGBuildOperations):
    @abstractmethod
    def perform_qa(self, questions: List[str]) -> List[str]:
        pass

class GraphRAGMINEOperations(GraphRAGBuildOperations):
    @abstractmethod
    def get_neighbour_triples(question: str, max_init_nodes: int = 8, max_depth: int = 2,
                              nodes_per_depth: int = 4, triples_per_node: int = 4,
                              triples_in_total: int = 64) -> List[str]:
        pass
