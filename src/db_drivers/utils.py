from typing import List, Tuple, Dict
from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from ..utils.errors import ReturnInfo

@dataclass
class BaseDatabaseConfig:
    #
    db_info: Dict = field(default_factory=lambda: {'db': 'default_db', 'table': 'default_table'})
    #
    params: Dict = field(default_factory=lambda: dict())
    #
    need_to_clear: bool = False

class AbstractDatabaseConnection(ABC):
    @abstractmethod
    def open_connection(self) -> ReturnInfo:
        """_summary_

        :return: _description_
        :rtype: ReturnInfo
        """
        # открытие соединения с бд
        pass

    @abstractmethod
    def is_open(self) -> bool:
        """_summary_

        :return: _description_
        :rtype: bool
        """
        pass

    @abstractmethod
    def close_connection(self) -> ReturnInfo:
        """_summary_

        :return: _description_
        :rtype: ReturnInfo
        """
        # закрытие соединения с бд
        pass

    @abstractmethod
    def create(self, items: List[object]) -> ReturnInfo:
        """_summary_

        :param items: _description_
        :type items: List[object]
        :return: _description_
        :rtype: ReturnInfo
        """

        # добавляем объект в бд
        # если он уже существует, то добавления не производим

        pass

    @abstractmethod
    def read(self, ids: List[str]) -> List[object]:
        """_summary_

        :param ids: _description_
        :type ids: List[str]
        :return: _description_
        :rtype: List[object]
        """

        # читаем объект из бд
        # если такого объекта не существует, то возвращаем None (список) (принтим предупреждение)

        pass

    @abstractmethod
    def update(self, items: List[object]) -> ReturnInfo:
        """_summary_

        :param items: _description_
        :type items: List[object]
        :return: _description_
        :rtype: ReturnInfo
        """

        # обновляем метаданные у объекта в бд
        # если такого объекта не существует, то пропускаем его (принтим предупреждение)

        pass

    @abstractmethod
    def delete(self, ids: List[object]) -> ReturnInfo:
        """_summary_

        :param ids: _description_
        :type ids: List[object]
        :return: _description_
        :rtype: ReturnInfo
        """

        # удаляем объект из бд
        # если его не существует, то пропускаем его (принтим предупреждение)

        pass

    @abstractmethod
    def count_items(self) -> object:
        """_summary_

        :return: _description_
        :rtype: object
        """
        # подсчёт количества объектов в таблицу бд
        pass

    @abstractmethod
    def item_exist(self, id: str) -> bool:
        """_summary_

        :param id: _description_
        :type id: str
        :return: _description_
        :rtype: bool
        """
        # проверка на существование объекта в бд
        pass

    @abstractmethod
    def clear(self) -> ReturnInfo:
        """_summary_

        :return: _description_
        :rtype: ReturnInfo
        """
        # Удаление содержания таблица базы данных, к которой было выполнено подключение
        pass

    def __del__(self):
        self.close_connection()
