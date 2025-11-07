from dataclasses import dataclass, field
from typing import Union, Dict

from .utils import VectorDBConnectionConfig, AbstractVectorDatabaseConnection
from .configs import DEFAULT_VECTORDB_CONFIGS, AVAILABLE_VECTORDB_CONNECTORS
from .embedders import EmbedderModel


@dataclass
class VectorDriverConfig:
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
        formated_config = VectorDriverConfig(**dict_config)
        formated_config.formate_fields()
        return formated_config


class VectorDriver:
    @staticmethod
    def connect(config: Union[Dict, VectorDriverConfig] = VectorDriverConfig(), embedder: Union[None, EmbedderModel] = None) -> AbstractVectorDatabaseConnection:
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
