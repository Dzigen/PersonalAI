from typing import Dict, Union
from dataclasses import dataclass

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
    def update_item_scores(self, mapping: Dict[str, int]) -> None:
        pass

    def delete_rare_items(self, num: int) -> None:
        pass
