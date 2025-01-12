from abc import  abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from ..utils import AbstractDatabaseConnection, BaseDatabaseConfig

@dataclass
class VectorDBConnectionConfig(BaseDatabaseConfig):
    path: str = None
    params: Dict = field(default_factory=lambda: {"hnsw:space": "ip"})

@dataclass
class VectorDBInstance:
    id: str = None
    document: str = None
    embedding: List[float] = None
    metadata: Dict = field(default_factory=lambda: dict())

class AbstractVectorDatabaseConnection(AbstractDatabaseConnection):
    @abstractmethod
    def retrieve(self, queries: List[VectorDBInstance], n_results: int = 50,
                 includes: List[str] = ['embeddings', 'documents', 'metadatas'], **kwargs) -> List[List[Tuple[float, VectorDBInstance]]]:
        """_summary_

        :param queries: _description_
        :type queries: List[VectorDBInstance]
        :param n_results: _description_, defaults to 50
        :type n_results: int, optional
        :param includes: _description_, defaults to ['embeddings', 'documents', 'metadatas']
        :type includes: List[str], optional
        :return: _description_
        :rtype: List[List[Tuple[float, VectorDBInstance]]]
        """
        # извлечение N ближайших сущностей к данной по заданной метрике
        pass
