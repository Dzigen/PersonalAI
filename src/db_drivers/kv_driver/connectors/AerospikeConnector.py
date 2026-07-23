from typing import List, Union, Dict
import aerospike

from .configs import DEFAULT_AEROSPIKE_CONFIG
from ..utils import KVDBConnectionConfig, AbstractKVDatabaseConnection, KeyValueDBInstance

# !!! AEROSPIKE IS NOT SUPPORTING DUE TO THE LACK OF DOCUMENTATION!!!


class AerospikeKVConnector(AbstractKVDatabaseConnection):

    def __init__(self, config: Union[Dict, KVDBConnectionConfig] = DEFAULT_AEROSPIKE_CONFIG):
        if isinstance(config, dict):
            config = KVDBConnectionConfig.from_dict(config)
        else:
            config.formate_fields()
        self.config: KVDBConnectionConfig = config

    def open_connection(self) -> None:
        db_config = {'hosts': [(self.config.host, self.config.port)]}
        if 'ports' in self.config.params:
            for ext_port in self.config.params['ports']:
                db_config['hosts'].append((self.config.host, ext_port))
        # print(db_config)
        self.client = aerospike.client(db_config).connect()

        if self.config.need_to_clear:
            self.clear()

    def is_open(self) -> bool:
        return self.client.is_connected()

    def close_connection(self) -> None:
        self.client.close()

    def create(self, items: List[KeyValueDBInstance]) -> None:
        for item in items:
            if item is None or item.id is None or item.value is None:
                raise ValueError(f"item: {item}")

            if not isinstance(item.id, str) or type(item.value) not in [str, float, int]:
                raise ValueError(f"item: {item}")

        for item in items:
            key = (self.config.db_info['db'],
                   self.config.db_info['table'], item.id)
            self.client.put(key, {'v': item.value})

    def read(self, ids: List[str]) -> List[KeyValueDBInstance]:
        for id in ids:
            if (id is None) or (not isinstance(id, str)):
                raise ValueError(f"* bad id:{id}\n* ids: {ids}")

        keys = list(map(lambda id: (
            self.config.db_info['db'], self.config.db_info['table'], id), ids))
        mixed_records = self.client.get_many(
            keys, policy={'total_timeout': 10000})
        records = [None if record[2] is None else KeyValueDBInstance(
            id=record[0][2], value=record[2]['v']) for record in mixed_records]
        return records

    def update(self, items: List[KeyValueDBInstance]) -> None:
        # TODO
        pass

    def delete(self, ids: List[str], durable_delete: bool = False) -> None:
        for id in ids:
            if not isinstance(id, str):
                raise ValueError(f"* bad id:{id}\n* ids: {ids}")

        keys = list(map(lambda id: (
            self.config.db_info['db'], self.config.db_info['table'], id), ids))
        self.client.batch_remove(keys, policy_batch_remove={
                                 'durable_delete': durable_delete})

    def clear(self) -> None:
        # TODO
        pass

    def item_exist(self, id: str) -> bool:
        if not isinstance(id, str):
            raise ValueError(f"id: {id}")

        key = (self.config.db_info['db'], self.config.db_info['table'], id)
        _, meta = self.client.exists(key)
        return False if meta is None else True

    def count_items(self) -> int:
        info = self.client.info_all("sets")
        node_values = list(info.items())[0][1][1]
        n_objects = node_values.split(":")[2].split('=')[1]
        return int(n_objects)
