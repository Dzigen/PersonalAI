from dataclasses import dataclass, field
from typing import Dict, Union
from copy import deepcopy

from .utils import TableDBConnectionConfig, AbstractTableDatabaseConnection
from .configs import DEFAULT_TABLEDB_CONFIGS, AVAILABLE_TABLEDB_CONNECTORS
from ...data_structs import BaseConfigOperations


@dataclass
class TableDriverConfig(BaseConfigOperations):
    """Конфигурация драйвера табличной базы данных.

    :param db_vendor: Идентификатор типа табличной БД (например, 'mysql', 'mongo', 'inmemory_table').
    :type db_vendor: str
    :param db_config: Конфигурация подключения к табличной БД, либо словарь с её параметрами.
    :type db_config: Union[Dict, TableDBConnectionConfig]
    """
    db_vendor: str = 'sqlite3'
    db_config: Union[Dict, TableDBConnectionConfig] = field(default_factory=lambda: DEFAULT_TABLEDB_CONFIGS['sqlite3'])

    def to_str(self):
        self.formate_fields()
        return f"{self.db_vendor}|{self.db_config.to_str()}"

    def formate_fields(self):
        if isinstance(self.db_config, dict):
            self.db_config = TableDBConnectionConfig.from_dict(self.db_config)

    @staticmethod
    def from_dict(dict_config: Dict):
        dictconfig_copy = deepcopy(dict_config)
        formated_config = TableDriverConfig(**dictconfig_copy)
        formated_config.formate_fields()
        return formated_config


class TableDriver:
    """Компонента для инициализации подключения к табличной базе данных."""
    @staticmethod
    def connect(config: Union[Dict, TableDriverConfig] = TableDriverConfig()) -> AbstractTableDatabaseConnection:
        """Метод предназначен для создания и открытия подключения к табличной БД.

        :param config: Конфигурация драйвера, либо словарь с её параметрами.
        :type config: Union[Dict, TableDriverConfig]
        :return: Открытое соединение с табличной БД, реализующее интерфейс AbstractTableDatabaseConnection.
        :rtype: AbstractTableDatabaseConnection
        """
        if isinstance(config, dict):
            config: TableDriverConfig = TableDriverConfig.from_dict(config)
        else:
            config.formate_fields()

        table_conn: AbstractTableDatabaseConnection = AVAILABLE_TABLEDB_CONNECTORS[config.db_vendor](config.db_config)
        table_conn.open_connection()
        return table_conn
