from typing import Dict, Tuple, List, Union
from dataclasses import dataclass, field
from abc import ABC, abstractmethod

@dataclass
class KVDBConnectionConfig:
    host: str
    port: str = None
    db_info: Dict = field(default_factory=lambda: dict())
    params: Dict = field(default_factory=lambda: dict())

@dataclass
class KeyValueDBInstance:
    id: str
    metadata: Dict

class AbstractKVDatabaseConnection(ABC):

    @abstractmethod
    def open_connection(self) -> None:
        # открытие соединения с бд
        pass

    @abstractmethod
    def is_open(self) -> bool:
        # Проверка наличия открытого соединения с базой
        pass

    @abstractmethod
    def close_connection(self) -> None:
        # закрытие соединения с бд
        pass

    @abstractmethod
    def create(self, item: List[KeyValueDBInstance]) -> None:
        # добавить вектора/метаданные/документы/идентификаторы
        pass

    @abstractmethod
    def read(self, ids: List[str]) -> List[KeyValueDBInstance]:
        # получить сущность по идентификатору
        pass

    @abstractmethod
    def update(self, items: List[KeyValueDBInstance]) -> None:
        pass

    @abstractmethod
    def delete(self, ids: List[str]) -> None:
        # удалить елементы по идентификатору
        pass

    @abstractmethod
    def clear(self) -> None:
        # Удаление содержания базы данных, которой было подключение
        pass

    @abstractmethod
    def item_exist(self, id: str) -> bool:
        # проверка на существование записи с данным ключом в бд
        pass

    @abstractmethod
    def count_items(self) -> int:
        # Получить текущее количество объектов в базе
        pass

    def __del__(self):
        self.close_connection()
