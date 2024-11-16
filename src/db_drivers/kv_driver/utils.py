from typing import Dict
from dataclasses import dataclass, field

from ..utils import AbstractDatabaseConnection, BaseDatabaseConfig

@dataclass
class KVDBConnectionConfig(BaseDatabaseConfig):
    host: str = None
    port: str = None

@dataclass
class KeyValueDBInstance:
    id: str
    metadata: Dict

class AbstractKVDatabaseConnection(AbstractDatabaseConnection):
    pass
