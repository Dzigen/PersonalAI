from typing import Dict
from dataclasses import dataclass, field

from ..utils import AbstractDatabaseConnection, BaseDatabaseConfig

@dataclass
class KVDBConnectionConfig(BaseDatabaseConfig):
    #: TODO
    host: str = None
    #: TODO
    port: str = None

@dataclass
class KeyValueDBInstance:
    #: TODO
    id: str
    #: TODO
    metadata: Dict

class AbstractKVDatabaseConnection(AbstractDatabaseConnection):
    """_summary_"""
    pass
