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
    def retrieve(self, queries: List[VectorDBInstance],
                 n_results: int, includes: List[str], **kwargs) -> List[List[Tuple[float, VectorDBInstance]]]:
        # извлечение N ближайших сущностей к данной по заданной метрике
        pass
