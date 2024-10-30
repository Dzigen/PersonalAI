from typing import Dict, Tuple, List
from dataclasses import dataclass, field
from abc import ABC, abstractmethod

@dataclass
class KVDBConnectionConfig:
    host: str
    port: str = None
    params: Dict = field(default_factory=lambda: {})

class AbstractKVDatabaseConnection(ABC):

    @abstractmethod
    def open_connection(self) -> None:
        """_summary_
        """
        # открытие соединения с бд
        pass

    @abstractmethod
    def close_connection(self) -> None:
        """_summary_
        """
        # закрытие соединения с бд
        pass

    @abstractmethod
    def create(self, key: Tuple, value: Dict) -> None:
        """_summary_

        :param key: _description_
        :type key: Tuple
        :param value: _description_
        :type value: Dict
        """
        # добавить вектора/метаданные/документы/идентификаторы
        pass

    @abstractmethod
    def delete(self, keys: List[Tuple], durable_delete: bool = False) -> None:
        """_summary_

        :param key_tuples: _description_
        :type key_tuples: List[Tuple]
        :param durable_delete: _description_, defaults to False
        :type durable_delete: bool, optional
        """
        # удалить елементы по идентификатору
        pass

    @abstractmethod
    def read(self, keys: List[Tuple]) -> List[Dict]:
        """_summary_

        :param key_tuples: _description_
        :type key_tuples: List[Tuple]
        :return: _description_
        :rtype: List[Dict]
        """
        # получить сущность по идентификатору
        pass

    @abstractmethod
    def clear(self, keys: List[Tuple]) -> None:
        """_summary_

        :param key_tuples: _description_
        :type key_tuples: List[Tuple]
        """
        # Удаление содержания заднной базы
        pass

    @abstractmethod
    def key_exist(self, key_tuple: Tuple) -> bool:
        """_summary_

        :param key_tuple: _description_
        :type key_tuple: Tuple
        :return: _description_
        :rtype: bool
        """
        # проверка на существование записи с данным ключом в бд
        pass

    @abstractmethod
    def count_instances(self) -> int:
        # Получить текущее количество объектов в базе
        pass

    def __del__(self):
        self.close_connection()
