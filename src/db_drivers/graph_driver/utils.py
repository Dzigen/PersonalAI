from typing import Dict
from dataclasses import dataclass, field
from abc import ABC, abstractmethod

@dataclass
class GraphDBConnectionConfig:
    uri: str = None
    params: Dict = field(default_factory=lambda: dict())

class AbstractGraphDatabaseConnection(ABC):
        
    @abstractmethod
    def open_connection(self) -> None:
        # открытие соединения с бд
        pass

    @abstractmethod
    def close_connection(self) -> None:
        # закрытие соединения с бд
        pass

    @abstractmethod
    def execute_query(self, query: str) -> object:
        pass

    def __del__(self):
        self.close_connection()