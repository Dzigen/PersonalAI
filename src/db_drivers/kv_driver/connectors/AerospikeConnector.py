from typing import List, Tuple, Dict
import aerospike

from ..utils import KVDBConnectionConfig, AbstractKVDatabaseConnection

DEFAULT_AEROSPIKE_CONFIG = KVDBConnectionConfig(host='aerospikelservice', port=3000)

class AerospikeConnector(AbstractKVDatabaseConnection):
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

    def close_connection(self) -> None:
        self.client.close()

    def create(self, key: Tuple, value: Dict) -> None:
        self.client.put(key, value)

    def delete(self, keys: List[Tuple], durable_delete: bool = False) -> None:
        self.client.batch_remove(keys, policy_batch_remove= {'durable_delete': durable_delete})

    def read(self, keys: List[Tuple]) -> List[Dict]:
        mixed_records = self.client.get_many(keys, policy={'total_timeout': 10000})
        records = [mixed_record[2] for mixed_record in mixed_records]
        return records

    def key_exist(self, key: Tuple) -> bool:
        _, meta = self.client.exists(key)
        return False if meta is None else True

    def count_instances(self) -> int:
        # TODO
        pass

    def clear(self, keys: List[Tuple]) -> None:
        # TODO
        pass
