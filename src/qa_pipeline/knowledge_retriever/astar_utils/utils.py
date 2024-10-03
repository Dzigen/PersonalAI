from typing import Dict
from dataclasses import dataclass, field
from abc import ABC, abstractmethod

from .AerospikeConnector import AerospikeConnector

@dataclass
class KVDBConnectionConfig:
    host: str
    port: str
    params: Dict = field(default_factory=lambda: {})

AVAILABLE_KVDB_CONNECTORS = {
    'aerospike': AerospikeConnector
}

DEFAULT_KVDB_CONFIGS = {
    'aerospike': field(default_factory=lambda: KVDBConnectionConfig(host='localhost', port=3000))
}

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

    def __del__(self):
        self.close_connection()