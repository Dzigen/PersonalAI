from typing import Dict, Union
from dataclasses import dataclass, field

from ..utils import AbstractDatabaseConnection, BaseDatabaseConfig


@dataclass
class KVDBConnectionConfig(BaseDatabaseConfig):
    db_info: Dict = field(default_factory=lambda: {'db': 'DefaultPersonalAIKVDB', 'table': 'DefaultPersonalAIKVTable'})
    host: str = None
    port: str = None

    def from_dict(dict_config) -> BaseDatabaseConfig:
        formated_config = KVDBConnectionConfig(**dict_config)
        formated_config.formate_fields()
        return formated_config

    def formate_fields(self):
        raw_redis_config = self.params.get('redis_config', None)
        if isinstance(raw_redis_config, Dict):
            self.params['redis_config'] = KVDBConnectionConfig.from_dict(self.params['redis_config'])
        raw_mongo_config = self.params.get('mongo_config', None)
        if isinstance(raw_mongo_config, Dict):
            self.params['mongo_config'] = KVDBConnectionConfig.from_dict(self.params['mongo_config'])


@dataclass
class KeyValueDBInstance:
    id: str
    value: Union[int, float, str, bytes]


class AbstractKVDatabaseConnection(AbstractDatabaseConnection):
    def update_item_scores(self, mapping: Dict[str, int]) -> None:
        """Метод предназначен для обновления оценок у хранящихся элементов в ордер-сете (Sorted Set).

        :param mapping:
        :type mapping: Dict[str, int]
        """

    def delete_rare_items(self, num: int) -> None:
        """Метод предназначен для удаления элементов, к которым было сделано наименьшее количество обращений.

        :param num: Количество элементов, которое нужно удалить.
        :type num: int
        """
