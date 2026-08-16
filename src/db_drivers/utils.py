from time import sleep
from typing import List, Dict
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from httpx import ConnectError, RemoteProtocolError, ConnectTimeout, ReadTimeout, ReadError

from ..utils.errors import ReturnInfo
from ..utils.data_structs import BaseConfigOperations


@dataclass
class BaseDatabaseConfig(BaseConfigOperations):
    """Базовая конфигурация для подключения к базе данных.

    :param db_info: Словарь, который должен хранить название базы данных и таблицы, к которой нужно подключиться. Значение по умолчанию {'db': 'DefaultPersonalAIDB', 'table': 'DefaultPersonalAITable'}.
    :type db_info: Dict
    :param params: Набор дополнительных гиперпараметров, который необходим для подключения и настройки бд. Значения по умолчанию dict().
    :type params: Dict
    :param need_to_clear: Если True, то после успешного подключения к базе данных содержимое указанной таблицы будет удалено, иначе False. Значения по умолчанию False.
    :type need_to_clear: bool
    :param create_index: Если True, то для требуемых элементов в бд будет создан индекс с целью повышения производительности поиска, иначе False. Значения по умолчанию False.
    :type create_index: bool
    :param timeout: ... . Значение по умолчанию 10.
    :type timeout: int
    :param trials: ... . Значение по умолчанию 5.
    :type trials: int
    """
    db_info: Dict = field(default_factory=lambda: {'db': 'DefaultPersonalAIDB', 'table': 'DefaultPersonalAITable'})
    params: Dict = field(default_factory=lambda: dict())
    need_to_clear: bool = False
    create_index: bool = False
    timeout: int = 10
    trials: int = 5

    @staticmethod
    def from_dict(dict_config: Dict):
        pass


class AbstractDatabaseCRUD(ABC):
    """Абстрактный интерфейс CRUD-операций над БД.

    Определяет минимальный набор методов (create/read/update/delete),
    который должен поддерживать любой конкретный драйвер базы данных.
    """
    @abstractmethod
    def create(self, items: List[object]) -> None:
        """Метод предназначен для добавления новых объектов в бд. Уникальность добавляемых объектов определяется по полю id.
        Если объект с таким id уже существует, то затирания информации не произойдёт: в бд останется прежний объект.

        :param items: Объекты на добавление.
        :type items: List[object]
        """
        pass

    @abstractmethod
    def read(self, ids: List[str], **kwargs) -> List[object]:
        """Метод предназначен для получения объектов из бд по их идентификаторам. Если такого идентификатора
        не существует, то он будет пропущен.

        :param ids: Идентификаторы объектов, которые нужно получить.
        :type ids: List[str]
        :return: Список запрошенных объектов.
        :rtype: List[object]
        """
        pass

    @abstractmethod
    def update(self, items: List[object]) -> None:
        """Метод предназначен для обновления значений у существующих ключей. Если данного ключа нет в базе,
        то элемент будет пропущен.

        :param items: _description_
        :type items: List[object]
        """
        pass

    @abstractmethod
    def delete(self, ids: List[str]) -> None:
        """Метод предназначен для удаления объектов из бд по их идентификаторам. Если такого идентификатора
        не существует, то он будет пропущен.

        :param ids: Идентификаторы объектов, которые нужно удалить.
        :type ids: List[str]
        """
        pass


class AbstractDatabaseExtendedOpt(ABC):
    """Абстрактный интерфейс расширенных операций над БД (подсчёт элементов, очистка, получение служебной информации)."""
    @abstractmethod
    def count_items(self) -> object:
        """Метод предназначен для получения суммарного количества элементов в таблице бд, к которой было выполнено подключение.

        :return: Структура данных, в которой хранится информация о количестве элементов.
        :rtype: object
        """
        pass

    @abstractmethod
    def item_exist(self, id: str) -> bool:
        """Метод предназначен для проверки на наличие объекта в бд по его идентификатору.

        :param id: Идентификатор объекта.
        :type id: str
        :return: Если объект существует, то True, иначе False.
        :rtype: bool
        """
        pass

    @abstractmethod
    def clear(self) -> None:
        """Метод предназначен для удаления содержания таблицы бд, к которой было выполнено подключение.
        """
        pass


class AbstractDatabaseInit(ABC):
    """Абстрактный интерфейс подключения к БД (открытие/закрытие соединения)."""

    config: BaseDatabaseConfig
    HANDLING_DB_EXCEPTIONS: List[Exception] = (
        ConnectionError, ConnectError, RemoteProtocolError,
        ConnectTimeout, ReadTimeout, ReadError, RuntimeError
    )

    @abstractmethod
    def open_connection(self) -> ReturnInfo:
        """Метод предназначен для подключения к бд.

        :return: Статус завершения операции с пояснительной информацией.
        :rtype: ReturnInfo
        """
        pass

    @abstractmethod
    def is_open(self) -> bool:
        """Метод предназначен для проверки статуса подключения к бд.

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


class AbstractDatabaseConnection(AbstractDatabaseCRUD, AbstractDatabaseExtendedOpt, AbstractDatabaseInit):
    """Интерфейс, который должен поддерживать класс взаимодействия с определённой базой данных."""
    pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close_connection()


def restore_connection(function):
    def wrapper(self: AbstractDatabaseInit, *args, **kwargs):
        flag, counter = True, 0
        while flag:
            try:
                output = function(self, *args, **kwargs)
                flag = False
            except self.HANDLING_DB_EXCEPTIONS as e:
                # print(f"Exception occuered {counter} / {self.config.trials}: ", str(e))
                counter += 1
                if counter > self.config.trials:
                    raise e
                else:
                    self.close_connection()
                    # print(f"Timeout: {self.config.timeout} sec")
                    sleep(self.config.timeout)
                    self.open_connection()

        return output
    return wrapper


def retry(function):
    def wrapper(self: AbstractDatabaseInit, *args, **kwargs):
        flag, counter = True, 0
        while flag:
            try:
                output = function(self, *args, **kwargs)
                flag = False
            except self.HANDLING_DB_EXCEPTIONS as e:
                # print(f"Exception occuered {counter} / {self.config.trials}: ", str(e))
                counter += 1
                if counter > self.config.trials:
                    raise e
                else:
                   # print(f"Timeout: {self.config.timeout} sec")
                    sleep(self.config.timeout)

        return output
    return wrapper
