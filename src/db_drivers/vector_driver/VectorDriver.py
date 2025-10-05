from dataclasses import dataclass, field
from typing import Union

from .utils import VectorDBConnectionConfig, AbstractVectorDatabaseConnection
from .configs import DEFAULT_VECTORDB_CONFIGS, AVAILABLE_VECTORDB_CONNECTORS
from .embedders import EmbedderModel


@dataclass
class VectorDriverConfig:
    db_vendor: str = 'chroma'
    vector_category: str = 'dense'  # 'dense' | 'sparse_bm25'
    db_config: VectorDBConnectionConfig = field(
        default_factory=lambda: DEFAULT_VECTORDB_CONFIGS['dense']['chroma'])


class VectorDriver:
    @staticmethod
    def connect(config: VectorDriverConfig = VectorDriverConfig(), embedder: Union[None, EmbedderModel] = None) -> AbstractVectorDatabaseConnection:

        connector_kw = config.db_vendor
        if config.vector_category.startswith("sparse"):
            connector_kw = f"{config.db_vendor}_{config.vector_category.split('_')[1]}"

        vector_conn = AVAILABLE_VECTORDB_CONNECTORS[connector_kw](config=config.db_config, embedder=embedder)
        vector_conn.open_connection()
        return vector_conn
