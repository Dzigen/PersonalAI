from typing import Dict
from dataclasses import dataclass, field

from ..utils import AbstractDatabaseConnection

@dataclass
class KVDBConnectionConfig:
    host: str
    port: str = None
    db_info: Dict = field(default_factory=lambda: {'db': 'default_db', 'table': 'default_table'})
    params: Dict = field(default_factory=lambda: dict())
    need_to_clear: bool = False

@dataclass
class KeyValueDBInstance:
    id: str
    metadata: Dict

class AbstractKVDatabaseConnection(AbstractDatabaseConnection):
    pass
