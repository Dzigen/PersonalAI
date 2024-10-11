from dataclasses import dataclass, field
from typing import Dict

from .utils import VectorDBConnectionConfig, AbstractVectorDatabaseConnection
from .configs import DEFAULT_VECTORDB_CONFIGS, AVAILABLE_VECTORDB_CONNECTORS

@dataclass
class VectorDriverConfig:
    db_vendor: str = 'chroma'
    db_config: VectorDBConnectionConfig = DEFAULT_VECTORDB_CONFIGS['chroma']

class VectorDriver:
    @staticmethod
    def connect(config: VectorDriverConfig = VectorDriverConfig()) -> AbstractVectorDatabaseConnection:
        return AVAILABLE_VECTORDB_CONNECTORS[config.db_vendor](config.db_config)