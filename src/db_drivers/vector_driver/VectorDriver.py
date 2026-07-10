from dataclasses import dataclass, field
from typing import Union, Dict
from copy import deepcopy

from .utils import VectorDBConnectionConfig, AbstractVectorDatabaseConnection
from .configs import DEFAULT_VECTORDB_CONFIGS, AVAILABLE_VECTORDB_CONNECTORS
from .embedders import EmbedderModel
from ...utils.data_structs import BaseConfigOperations


@dataclass
class VectorDriverConfig(BaseConfigOperations):
    """Конфигурация драйвера векторного хранилища.

    :param db_vendor: Идентификатор конкретного провайдера векторного хранилища (например, 'chroma', 'milvus', 'elasticsearch', 'inmemory').
    :type db_vendor: str
    :param vector_category: Категория векторного хранилища ('dense' для плотных эмбеддингов, 'sparse_bm25' для разреженных BM25-представлений).
    :type vector_category: str
    :param db_config: Конфигурация подключения к выбранному хранилищу, либо словарь с её параметрами.
    :type db_config: VectorDBConnectionConfig
    """
    db_vendor: str = 'chroma'
    vector_category: str = 'dense'  # 'dense' | 'sparse_bm25'
    db_config: VectorDBConnectionConfig = field(default_factory=lambda: DEFAULT_VECTORDB_CONFIGS['dense']['chroma'])

    def to_str(self):
        self.formate_fields()
        return f"{self.db_vendor}|{self.db_config.to_str()}"

    def formate_fields(self):
        if isinstance(self.db_config, dict):
            self.db_config = VectorDBConnectionConfig.from_dict(self.db_config)

    @staticmethod
    def from_dict(dict_config: Dict):
        dictconfig_copy = deepcopy(dict_config)
        formated_config = VectorDriverConfig(**dictconfig_copy)
        formated_config.formate_fields()
        return formated_config


class VectorDriver:
    """Компонента для инициализации подключения к векторному хранилищу."""
    @staticmethod
    def connect(config: Union[Dict, VectorDriverConfig] = VectorDriverConfig(), embedder: Union[None, EmbedderModel] = None) -> AbstractVectorDatabaseConnection:
        """Метод предназначен для создания и открытия подключения к векторному хранилищу.

        :param config: Конфигурация драйвера (VectorDriverConfig), либо словарь с её параметрами.
        :type config: Union[Dict, VectorDriverConfig]
        :param embedder: Класс для получения эмбеддингов (EmbedderModel).
        :type embedder: Union[None, EmbedderModel]
        :return: Открытое соединение с векторным хранилищем, реализующее интерфейс AbstractVectorDatabaseConnection.
        :rtype: AbstractVectorDatabaseConnection
        """
        if isinstance(config, dict):
            config: VectorDriverConfig = VectorDriverConfig.from_dict(config)
        else:
            config.formate_fields()

        connector_kw = config.db_vendor
        if config.vector_category.startswith("sparse"):
            connector_kw = f"{config.db_vendor}_{config.vector_category.split('_')[1]}"

        vector_conn: AbstractVectorDatabaseConnection = AVAILABLE_VECTORDB_CONNECTORS[connector_kw](config=config.db_config, embedder=embedder)
        vector_conn.open_connection()
        return vector_conn
