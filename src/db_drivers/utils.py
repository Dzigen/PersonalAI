from typing import List, Tuple, Dict
from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from ..utils.errors import ReturnInfo

@dataclass
class BaseDatabaseConfig:
    #: TODO
    db_info: Dict = field(default_factory=lambda: {'db': 'default_db', 'table': 'default_table'})
    #: TODO
    params: Dict = field(default_factory=lambda: dict())
    #: TODO
    need_to_clear: bool = False

class AbstractDatabaseConnection(ABC):
    @abstractmethod
    def open_connection(self) -> ReturnInfo:
        """Метод предназначен для подключения бд.

        :return: Статус завершения операции с пояснительной информацией.
        :rtype: ReturnInfo
        """
        pass

    @abstractmethod
    def is_open(self) -> bool:
        """Метод предназначен для проверки состояния соединения с бд.

        :return: Если True, то соединение с бд есть, иначе False.
        :rtype: bool
        """
        pass

    @abstractmethod
    def close_connection(self) -> ReturnInfo:
        """Метод предназначен для разрыва соединения с бд.

        :return: Статус завершения операции с пояснительной информацией.
        :rtype: ReturnInfo
        """
        pass

    @abstractmethod
    def create(self, items: List[object]) -> ReturnInfo:
        """Метод предназначен для добавления новых объектов в бд. Уникальность добавлемых объектов определяется по полю id.
        Если объект с таким id уже существует, то затирания информации не произойдёт: в бд останется прежний объект.

        :param items: Объект на добавление
        :type items: List[object]
        :return: Статус завершения операции с пояснительной информацией.
        :rtype: ReturnInfo
        """
        pass

    @abstractmethod
    def read(self, ids: List[str]) -> List[object]:
        """Метод предназначен для получения объектов из бд по их идентификаторам. Если такого идентификатора
        не существует, то он будет пропущен.

        :param ids: Идентификаторы объектов, которые нужно получить.
        :type ids: List[str]
        :return: Список запрошенных объектов.
        :rtype: List[object]
        """
        pass

    @abstractmethod
    def update(self, items: List[object]) -> ReturnInfo:
        pass

    @abstractmethod
    def delete(self, ids: List[str]) -> ReturnInfo:
        """Метод предназначен для удления объектов из бд по их идентификаторам. Если такого идентификатора
        не существует, то он будет пропущен.

        :param ids: Идентификаторы объектов, которые нужно удалить.
        :type ids: List[object]
        :return: Статус завершения операции с пояснительной информацией.
        :rtype: ReturnInfo
        """
        pass

    @abstractmethod
    def count_items(self) -> object:
        """Метод предназначен для получения количества элементов в таблице бд, которой было выполнено подключение.

        :return: Структура данных, в которой хранится информация о количестве объектов.
        :rtype: object
        """
        pass

    @abstractmethod
    def item_exist(self, id: str) -> bool:
        """Метод предназначен для проверки на наличие объекта в бд по его идентификатору.

        :param id: Иднетификатор объекта.
        :type id: str
        :return: Если объект существуюет, то True, иначе False.
        :rtype: bool
        """
        pass

    @abstractmethod
    def clear(self) -> ReturnInfo:
        """Метод предназначен для удаления содержания таблицы в бд, которой было выполнено подключение.

        :return: _description_
        :rtype: ReturnInfo
        """
        pass

    def __del__(self):
        self.close_connection()
