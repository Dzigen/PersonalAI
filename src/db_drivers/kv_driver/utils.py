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
        """ Обновляем скоры использования элементов в ордер сете.

        :param mapping:
        :type mapping: Dict[str, int]
        """

    def delete_rare_items(self, num: int) -> None:
        """Удаляем элементы, к которым было сделано наименьшее количество обращений.

        :param num: Количество элементов, которое нужно удалить.
        :type num: int
        """
