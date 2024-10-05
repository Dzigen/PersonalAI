from typing import Dict
from dataclasses import dataclass, field
from abc import ABC, abstractmethod

@dataclass
class KVDBConnectionConfig:
    host: str
    port: str
    params: Dict = field(default_factory=lambda: {})

class AbstractKVDatabaseConnection(ABC):
        
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
    def read(self):
        # получить сущность по идентификатору 
        pass

    @abstractmethod
    def clear(self):
        # Удаление содержания заднной базы 
        pass

    @abstractmethod
    def key_exist(self):
        # проверка на существование записи с данным ключом в бд
        pass

    def __del__(self):
        self.close_connection()