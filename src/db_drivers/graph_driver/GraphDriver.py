from dataclasses import dataclass, field
from typing import Dict, Union
from copy import deepcopy

from .utils import GraphDBConnectionConfig, AbstractGraphDatabaseConnection
from .configs import DEFAULT_GRAPHDB_CONFIGS, AVAILABLE_GRAPHDB_CONNECTORS
from ...utils.data_structs import BaseConfigOperations


@dataclass
class GraphDriverConfig(BaseConfigOperations):
    """Конфигурация драйвера графовой базы данных.

    :param db_vendor: Идентификатор типа графовой БД.
    :type db_vendor: str
    :param db_config: Конфигурация подключения к графовой БД, либо словарь с параметрами, который будет преобразован в GraphDBConnectionConfig.
    :type db_config: Union[Dict, GraphDBConnectionConfig]
    """
    db_vendor: str = 'kuzu'
    db_config: Union[Dict, GraphDBConnectionConfig] = field(default_factory=lambda: DEFAULT_GRAPHDB_CONFIGS['kuzu'])

    def to_str(self):
        self.formate_fields()
        return f"{self.db_vendor}|{self.db_config.to_str()}"

    def formate_fields(self):
        if isinstance(self.db_config, dict):
            self.db_config = GraphDBConnectionConfig.from_dict(self.db_config)

    @staticmethod
    def from_dict(dict_config: Dict):
        dictconfig_copy = deepcopy(dict_config)
        formated_config = GraphDriverConfig(**dictconfig_copy)
        formated_config.formate_fields()
        return formated_config


class GraphDriver:
    """Компонента для инициализации подключения к графовой базе данных."""
    @staticmethod
    def connect(config: Union[Dict, GraphDriverConfig] = GraphDriverConfig()) -> AbstractGraphDatabaseConnection:
        """Метод предназначен для создания и открытия подключения к графовой БД.

        :param config: Конфигурация драйвера (GraphDriverConfig) либо словарь с её параметрами.
        :type config: Union[Dict, GraphDriverConfig]
        :return: Открытое соединение с графовой базой данных, реализующее интерфейс AbstractGraphDatabaseConnection.
        :rtype: AbstractGraphDatabaseConnection
        """
        if isinstance(config, dict):
            config: GraphDriverConfig = GraphDriverConfig.from_dict(config)
        else:
            config.formate_fields()

        graph_conn: AbstractGraphDatabaseConnection = AVAILABLE_GRAPHDB_CONNECTORS[config.db_vendor](config.db_config)
        graph_conn.open_connection()
        return graph_conn
