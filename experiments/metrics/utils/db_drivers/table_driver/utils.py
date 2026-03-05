from typing import Dict, Union, Tuple, List
from dataclasses import dataclass, field
from copy import deepcopy

from ..utils import AbstractDatabaseConnection, BaseDatabaseConfig


@dataclass
class TableDBConnectionConfig(BaseDatabaseConfig):
    """Конфигурация подключения к табличной базе данных.

    :param db_info: Информация о базе и таблице, используемой для хранения данных. По умолчанию {'db': 'DefaultPersonalAITableDB', 'table': 'DefaultPersonalAITable'}).
    :type db_info: Dict
    :param host: Хост, на котором развернута табличная БД.
    :type host: str
    :param port: Порт, по которому производится подключение к табличной БД.
    :type port: str
    """
    db_info: Dict = field(default_factory=lambda: {'db': 'DefaultPersonalAITableDB', 'table': 'DefaultPersonalAITable'})
    host: str = None
    port: str = None

    def to_str(self):
        str_hostport = f"{self.host};{self.port}"
        str_needto = f"{self.need_to_clear};{self.create_index}"
        return f"{self.db_info};{str_hostport};{str_needto};{self.params}"

    @staticmethod
    def from_dict(dict_config: Dict):
        dictconfig_copy = deepcopy(dict_config)
        formated_config = TableDBConnectionConfig(**dictconfig_copy)
        formated_config.formate_fields()
        return formated_config


@dataclass
class BaseTableStucture:
    """Базовый класс для описания структуры записей, хранящихся в табличной БД."""
    pass


@dataclass
class TableDBInstance:
    """Структура данных для представления одной записи табличной БД.

    :param values: Объект со значениями полей записи.
    :type values: BaseTableStucture
    :param id: Уникальный идентификатор записи (строковое значение) либо None, если идентификатор ещё не задан.
    :type id: Union[None, str]
    """
    values: BaseTableStucture
    id: Union[None, str] = None


class AbstractTableDatabaseConnection(AbstractDatabaseConnection):
    """Абстрактный интерфейс для взаимодействия с табличной базой данных.

    Определяет базовую структуру данных и проверки корректности записей/идентификаторов, а также метод для создания таблиц.
    """
    TABLE_STRUCTURE: BaseTableStucture = None

    def create_table(self, query: str, params: Tuple[object]) -> None:
        """Метод предназначен для создания или инициализации таблицы.

        :param query: запрос для создания таблицы.
        :type query: str
        :param params: Параметры для запроса, если они требуются.
        :type params: Tuple[object]
        """
        pass

    def validate_items(self, items: List[TableDBInstance]) -> bool:
        """Метод предназначен для валидации списка записей перед сохранением в табличную БД.

        :param items: Список объектов, представляющих записи в табличной БД.
        :type items: List[TableDBInstance]
        :return: True, если все записи прошли проверку, иначе - исключение.
        :rtype: bool
        """
        if self.TABLE_STRUCTURE is None:
            raise ValueError
        for item in items:
            if not isinstance(item.values, self.TABLE_STRUCTURE):
                raise TypeError
            if item.id is not None and not isinstance(item.id, str):
                raise TypeError

        not_null_ids = [item.id for item in items if item.id is not None]
        unique_ids_wo_null = set(not_null_ids)
        if len(not_null_ids) != len(unique_ids_wo_null):
            raise ValueError

        return True

    def validate_ids(self, ids: List[str]) -> bool:
        """Метод предназначен для валидации списка идентификаторов записей.

        :param ids: Список идентификаторов записей.
        :type ids: List[str]
        :return: True, если все идентификаторы прошли проверку, иначе - исключение.
        """
        for id in ids:
            if (id is None) or (not isinstance(id, str)):
                raise ValueError

        return True
