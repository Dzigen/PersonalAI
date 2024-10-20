from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List

class AbstractVectorDatabaseConnection(ABC):
    
    @abstractmethod
    def open_connection(self):
        # открытие соединения с бд
        pass

    @abstractmethod
    def close_connection(self):
        # закрытие соединения с бд
        pass

    @abstractmethod
    def create(self):
        # добавить вектора/метаданные/документы/идентификаторы
        pass

    @abstractmethod
    def delete(self):
        # удалить елементы по идентификатору
        pass

    @abstractmethod
    def update(self):
        # обновить документ/метаданные для конкретной сущности в базе
        pass

    @abstractmethod
    def read(self):
        # получить сущность по идентификатору 
        pass

    @abstractmethod
    def retrieve(self):
        # извлечение N ближайших сущностей к данной по заданной метрике
        pass

    @abstractmethod
    def clear(self):
        # Удаление содержания заднной базы 
        pass

    def __del__(self):
        self.close_connection()

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