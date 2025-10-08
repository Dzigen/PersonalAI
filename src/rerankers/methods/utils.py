from typing import List, Union, Tuple
from abc import ABC, abstractmethod
from ...db_drivers.vector_driver import VectorDBInstance


class AbstractRerankerModule(ABC):

    @abstractmethod
    def run(self, query: str, top_k: int = 1, subset_ids: Union[None, List[str]] = None,
            includes: List[str] = ['documents', 'metadatas'], return_with_embeddings: bool = False,
            return_with_scores: bool = False) -> Union[List[Tuple[float, VectorDBInstance]], List[VectorDBInstance]]:
        # TODO
        pass
