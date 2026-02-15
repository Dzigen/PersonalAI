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

    @abstractmethod
    @staticmethod
    def prepare_kgbuild_env_params(self, conn_params: Dict, hyperp_params: Dict) -> List[Dict[str,str]]:
        pass

class GraphRAGQAOperations(GraphRAGBuildOperations):

    def __init__(self, memory_config: Dict, qa_config: Dict) -> None:
        pass

    @abstractmethod
    def perform_qa(self, questions: List[str]) -> List[str]:
        pass

    @abstractmethod
    @staticmethod
    def prepare_qaeval_env_params(self, conn_params: Dict, hyperp_params: Dict) -> List[Dict[str,str]]:
        pass

    @abstractmethod
    @staticmethod
    def prepare_qa_config(self) -> Dict:
        pass

class GraphRAGMINEOperations(GraphRAGBuildOperations):
    @abstractmethod
    def get_neighbour_triples(question: str, max_init_nodes: int = 8, max_depth: int = 2,
                              nodes_per_depth: int = 4, triples_per_node: int = 4,
                              triples_in_total: int = 64) -> List[str]:
        pass

    @abstractmethod
    @staticmethod
    def prepare_kgeval_mine_env_params(self, conn_params: Dict, hyperp_params: Dict) -> List[Dict[str,str]]:
        pass
