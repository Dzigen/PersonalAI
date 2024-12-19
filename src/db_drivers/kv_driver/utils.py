from typing import Dict, Union
from dataclasses import dataclass, field

from ..utils import AbstractDatabaseConnection, BaseDatabaseConfig

@dataclass
class KVDBConnectionConfig(BaseDatabaseConfig):
    host: str = None
    port: str = None

@dataclass
class KeyValueDBInstance:
    id: str
    value: Union[int, float, str]

class AbstractKVDatabaseConnection(AbstractDatabaseConnection):
    pass
