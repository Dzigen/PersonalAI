from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

@dataclass
class VectorDBConnectionConfig:
    path: str
    db_name: str
    params: Dict = field(default_factory=lambda: {"hnsw:space": "ip"})
    need_to_clear: bool = False

@dataclass
class VectorDBInstance:
    id: str = None
    document: str = None
    embedding: List[float] = None
    metadata: Dict = field(default_factory=lambda: dict())

class AbstractVectorDatabaseConnection(ABC):

    @abstractmethod
    def open_connection(self) -> None:
        """_summary_
        """
        # открытие соединения с бд
        pass

    @abstractmethod
    def is_open(self) -> bool:
        # Проверка наличия открытого соединения с базой
        pass

    @abstractmethod
    def close_connection(self) -> None:
        """_summary_
        """
        # закрытие соединения с бд
        pass

    @abstractmethod
    def create(self, items: List[VectorDBInstance], **kwargs) -> None:
        # добавить вектора/метаданные/документы/идентификаторы
        pass

    @abstractmethod
    def read(self, ids: List[str], includes: List[str], **kwargs) -> List[VectorDBInstance]:
        # получить сущность по идентификатору
        pass

    @abstractmethod
    def update(self, items: List[VectorDBInstance], **kwargs) -> None:
        # обновить документ/метаданные для конкретной сущности в базе
        pass

    @abstractmethod
    def delete(self, ids: List[str], **kwargs):
        # удалить елементы по идентификатору
        pass

    @abstractmethod
    def retrieve(self, queries: List[VectorDBInstance],
                 n_results: int, includes: List[str], **kwargs) -> List[List[Tuple[float, VectorDBInstance]]]:
        # извлечение N ближайших сущностей к данной по заданной метрике
        pass

    @abstractmethod
    def clear(self) -> None:
        # Удаление содержания заднной базы
        pass

    @abstractmethod
    def count_instances(self) -> int:
        # Получить текущее количество объектов в базе
        pass

    def __del__(self):
        self.close_connection()
