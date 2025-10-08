from abc import abstractmethod, ABC
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Tuple, Union

from ..utils import AbstractDatabaseConnection, AbstractDatabaseConnection, BaseDatabaseConfig


@dataclass
class VectorDBConnectionConfig(BaseDatabaseConfig):
    db_info: Dict = field(default_factory=lambda: {
                          'db': 'defaultpersonalaivectordb', 'table': 'defaultpersonalaivectortable'})
    conn: Dict = field(default_factory=lambda: dict())


@dataclass
class VectorDBInstance:
    id: Union[None, str] = None
    document: Union[None, str] = None
    embedding: Union[None, List[float]] = None
    metadata: Dict = field(default_factory=lambda: dict())

    def to_dict(self):
        return {k: v for k, v in asdict(self).items()}


class AbstractVectorDatabaseConnection(AbstractDatabaseConnection):
    @abstractmethod
    def retrieve(self, query_instances: List[VectorDBInstance], n_results: int = 50, subset_ids: Union[None, List[str]] = None,
                 includes: List[str] = ['embeddings', 'documents', 'metadatas']) -> List[List[Tuple[float, VectorDBInstance]]]:
        # извлечение N ближайших сущностей к данной по заданной метрике
        pass

    @abstractmethod
    def upsert(self, items: List[VectorDBInstance]) -> None:
        pass


class AbstractVectorDatabaseComposer(AbstractDatabaseConnection):

    @abstractmethod
    def check_consistency(self) -> bool:
        pass

    @abstractmethod
    def upsert(self, items: List[VectorDBInstance]) -> None:
        pass
