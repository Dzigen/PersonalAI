from typing import List, Tuple, Dict
import aerospike 

from .utils import KVDBConnectionConfig, AbstractKVDatabaseConnection

DEFAULT_AEROSPIKE_CONFIG = KVDBConnectionConfig(host='aerospikelservice', port=3000)

class AerospikeConnector(AbstractKVDatabaseConnection):
    def __init__(self, config: KVDBConnectionConfig = DEFAULT_AEROSPIKE_CONFIG):
        self.config = config
        self.open_connection()

    def open_connection(self):
        db_config = {'hosts': [(self.config.host, self.config.port)]}
        if 'ports' in self.config.params:
            for ext_port in self.config.params['ports']:
                db_config['hosts'].append((self.config.host, ext_port))
        print(db_config)
        self.client = aerospike.client(db_config).connect()
        
    def close_connection(self):
        self.client.close()

    def create(self, key_tuples: List[Tuple], values: List[Dict]):
        for k, v in zip(key_tuples, values):
            self.client.put(k, v)

    def delete(self, key_tuples: List[Tuple], durable_delete: bool = False):
        self.client.batch_remove(key_tuples, policy_batch_remove= {'durable_delete': durable_delete})

    def read(self, key_tuples: List[Tuple]):
        mixed_records = self.client.get_many(key_tuples)
        records = [mixed_record[2] for mixed_record in mixed_records]
        return records
    
    def key_exist(self, key_tuple: Tuple) -> bool:
        _, meta = self.client.exists(key_tuple)
        return False if meta is None else True

    def clear(self, key_tuples: List[Tuple]):
        # TODO
        pass