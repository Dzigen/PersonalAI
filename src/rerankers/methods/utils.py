from typing import List, Union
from abc import ABC, abstractmethod
from ...db_drivers.vector_driver import VectorDBInstance


class AbstractRerankerModule(ABC):

    @abstractmethod
    def run(self, query: str, top_k: int = 1, return_with_embeddings: Union[str, bool] = False) -> List[VectorDBInstance]:
        # TODO
        pass
