from typing import List, Tuple
from abc import ABC, abstractmethod

from ..utils.errors import ReturnInfo

class AbstractDatabaseConnection(ABC):
    @abstractmethod
    def open_connection(self) -> ReturnInfo:
        # открытие соединения с бд
        pass

    @abstractmethod
    def is_open(self) -> bool:
        #
        pass

    @abstractmethod
    def close_connection(self) -> ReturnInfo:
        # закрытие соединения с бд
        pass

    @abstractmethod
    def create(self, items: List[object]) -> ReturnInfo:
        """_summary_

        :param triplet: _description_
        :type triplet: Triplet
        """

        # добавляем объект в бд
        # если он уже существует, то добавления не производим

        pass

    @abstractmethod
    def read(self, ids: List[str]) -> List[object]:

        # читаем объект из бд
        # если такого объекта не существует, то возвращаем None (список) (принтим предупреждение)

        pass

    @abstractmethod
    def update(self, items: List[object]) -> ReturnInfo:

        # обновляем метаданные у объекта в бд
        # если такого объекта не существует, то пропускаем его (принтим предупреждение)

        pass

    @abstractmethod
    def delete(self, ids: List[object]) -> ReturnInfo:
        """_summary_

        :param triplet: _description_
        :type triplet: Triplet
        """

        # удаляем объект из бд
        # если его не существует, то пропускаем его (принтим предупреждение)

        pass

    @abstractmethod
    def count_items(self) -> int:
        # подсчёт количества объектов в таблицу бд
        pass

    @abstractmethod
    def item_exist(self, id: str) -> bool:
        # проверка на существование объекта в бд
        pass

    @abstractmethod
    def clear(self) -> ReturnInfo:
        # Удаление содержания таблица базы данных, к которой было выполнено подключение
        pass

    def __del__(self):
        self.close_connection()
