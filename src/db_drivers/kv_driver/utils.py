from typing import Dict
from dataclasses import dataclass, field

from ..utils import AbstractDatabaseConnection, BaseDatabaseConfig

@dataclass
class KVDBConnectionConfig(BaseDatabaseConfig):
    #
    host: str
    #
    port: str = None

@dataclass
class KeyValueDBInstance:
    #
    id: str
    #
    metadata: Dict

class AbstractKVDatabaseConnection(AbstractDatabaseConnection):
    """_summary_"""
    pass
