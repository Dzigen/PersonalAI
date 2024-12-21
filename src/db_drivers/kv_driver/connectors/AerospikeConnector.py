from typing import List, Tuple, Dict
import aerospike

from ..utils import KeyValueDBInstance
from ..utils import KVDBConnectionConfig, AbstractKVDatabaseConnection

DEFAULT_AEROSPIKE_CONFIG = KVDBConnectionConfig(host='aerospikelservice', port=3000)

class AerospikeKVConnector(AbstractKVDatabaseConnection):

    def __init__(self, config: KVDBConnectionConfig = DEFAULT_AEROSPIKE_CONFIG):
        self.config = config
        self.open_connection()

    def open_connection(self) -> None:
        db_config = {'hosts': [(self.config.host, self.config.port)]}
        if 'ports' in self.config.params:
            for ext_port in self.config.params['ports']:
                db_config['hosts'].append((self.config.host, ext_port))
        print(db_config)
        self.client = aerospike.client(db_config).connect()

    def is_open(self) -> bool:
        return self.client.is_connected()

    def close_connection(self) -> None:
        self.client.close()

    def create(self, items: List[KeyValueDBInstance]) -> None:
        for item in items:
            if item is None or item.id is None or item.value is None:
                raise ValueError

            if type(item.id) is not str or type(item.value) not in [str, float, int]:
                raise ValueError

        for item in items:
            key = (self.config.db_info['db'], self.config.db_info['table'], item.id)
            self.client.put(key, {'v': item.value})

    def read(self, ids: List[str]) -> List[KeyValueDBInstance]:
        for id in ids:
            if (id is None) or (type(id) is not str):
                raise ValueError

        keys = list(map(lambda id: (self.config.db_info['db'], self.config.db_info['table'], id), ids))
        mixed_records = self.client.get_many(keys, policy={'total_timeout': 10000})
        records = [KeyValueDBInstance(id=record[0][2], metadata=record[2]['v']) for record in mixed_records]
        return records

    def update(self, items: List[KeyValueDBInstance]) -> None:
        # TODO
        pass

    def delete(self, ids: List[str], durable_delete: bool = False) -> None:
        for id in ids:
            if type(id) is not str:
                raise ValueError

        keys = list(map(lambda id: (self.config.db_info['db'], self.config.db_info['table'], id), ids))
        self.client.batch_remove(keys, policy_batch_remove= {'durable_delete': durable_delete})

    def clear(self) -> None:
        # TODO
        pass

    def item_exist(self, id: str) -> bool:
        if type(id) is not str:
            raise ValueError

        key = (self.config.db_info['db'], self.config.db_info['table'], id)
        _, meta = self.client.exists(key)
        return False if meta is None else True

    def count_items(self) -> int:
        # TODO
        pass
