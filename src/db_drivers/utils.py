from typing import List
from abc import ABC, abstractmethod

class AbstractDatabaseConnection(ABC):
    @abstractmethod
    def open_connection(self) -> None:
        # открытие соединения с бд
        pass

    @abstractmethod
    def is_open(self) -> None:
        #
        pass

    @abstractmethod
    def close_connection(self) -> None:
        # закрытие соединения с бд
        pass

    @abstractmethod
    def create(self, items: List[object]) -> None:
        """_summary_

        :param triplet: _description_
        :type triplet: Triplet
        """
        pass

    @abstractmethod
    def read(self, ids: List[str]) -> List[object]:
        pass

    @abstractmethod
    def update(self, items: List[object]) -> None:
        pass

    @abstractmethod
    def delete(self, ids: List[object]) -> None:
        """_summary_

        :param triplet: _description_
        :type triplet: Triplet
        """
        pass

    @abstractmethod
    def count_items(self) -> int:
        pass

    @abstractmethod
    def item_exist(self, id: str) -> bool:
        # проверка на существование записи с данным ключом в бд
        pass

    @abstractmethod
    def clear(self) -> None:
        # Удаление содержания базы данных, которой было подключение
        pass

    def __del__(self):
        self.close_connection()
