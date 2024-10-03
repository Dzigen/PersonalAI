from typing import List, Tuple, Dict
import aerospike 

from .utils import KVDBConnectionConfig, AbstractKVDatabaseConnection

class AerospikeConnector(AbstractKVDatabaseConnection):
    def __init__(self, config: KVDBConnectionConfig):
        self.config = config

    def open_connection(self):
        db_config = {'hosts': [(self.config.host, self.config.port)]}
        self.client = aerospike.client(db_config).connect()
        
    def close_connection(self):
        self.client.close()

    def create(self, key_tuples: List[Tuple], values: List[Dict]):
        for k, v in zip(key_tuples, values):
            self.client.put(k, v)

    def delete(self, key_tuples: List[Tuple]):
        self.client.batch_remove(key_tuples)

    def read(self, key_tuples: List[Tuple]):
        mixed_records = self.client.get_many(key_tuples)
        records = [mixed_record[3] for mixed_record in mixed_records]
        return records

    def clear(self, key_tuples: List[Tuple]):
        self.client.batch_remove(key_tuples)