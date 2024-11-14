from dataclasses import dataclass, field
from typing import Dict

from .utils import VectorDBConnectionConfig, AbstractVectorDatabaseConnection
from .configs import DEFAULT_VECTORDB_CONFIGS, AVAILABLE_VECTORDB_CONNECTORS

@dataclass
class VectorDriverConfig:
    #: TODO
    db_vendor: str = 'chroma'
    #: TODO
    db_config: VectorDBConnectionConfig = field(default_factory=lambda: DEFAULT_VECTORDB_CONFIGS['chroma'])

class VectorDriver:
    """_summary_"""
    @staticmethod
    def connect(config: VectorDriverConfig = VectorDriverConfig()) -> AbstractVectorDatabaseConnection:
        return AVAILABLE_VECTORDB_CONNECTORS[config.db_vendor](config.db_config)
