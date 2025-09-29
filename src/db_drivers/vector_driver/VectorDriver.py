from dataclasses import dataclass, field

from .utils import VectorDBConnectionConfig, AbstractVectorDatabaseConnection
from .configs import DEFAULT_VECTORDB_CONFIGS, AVAILABLE_VECTORDB_CONNECTORS


@dataclass
class VectorDriverConfig:
    db_vendor: str = 'chroma'
    vector_category: str = 'dense'  # 'dense' | 'sparse_bm25'
    db_config: VectorDBConnectionConfig = field(
        default_factory=lambda: DEFAULT_VECTORDB_CONFIGS['dense']['chroma'])


class VectorDriver:
    @staticmethod
    def connect(config: VectorDriverConfig = VectorDriverConfig()) -> AbstractVectorDatabaseConnection:

        connector_kw = config.db_vendor
        if config.vector_category.startswith("sparse"):
            connector_kw = f"{config.db_vendor}_{config.vector_category.split("_")[1]}"

        vector_conn = AVAILABLE_VECTORDB_CONNECTORS[connector_kw](
            config.db_config)
        vector_conn.open_connection()
        return vector_conn
