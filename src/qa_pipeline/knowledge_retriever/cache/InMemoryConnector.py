from typing import List, Tuple, Dict
import gc
import joblib

from .utils import KVDBConnectionConfig, AbstractKVDatabaseConnection

DEFAULT_INMEMORY_CONFIG = KVDBConnectionConfig(
    host='localhost', 
    params={'kvstore_dump_name': 'inmemory_store.dump', 'load_from_disk': False})

class InMemoryConnector(AbstractKVDatabaseConnection):
    
    def __init__(self, config: KVDBConnectionConfig = DEFAULT_INMEMORY_CONFIG) -> None:
        self.config = config
        self.open_connection(load_from_disk=self.config.params['load_from_disk'])

    def open_connection(self, load_from_disk: bool = False, kvstore_dump_dir: str = '.') -> None:
        if load_from_disk:
            self.kv_store = joblib.loads(f"{kvstore_dump_dir}/{self.config.params['kvstore_dump_name']}")
        else:
            self.kv_store = dict()

    def close_connection(self, save_on_disk: bool = True):
        if save_on_disk:
            joblib.dump(self.kv_store, self.config.params['save_store_path'])
        del self.kv_store

    def create(self, keys: List[object], values: List[str]):
        for k, v in zip(keys, values):
            self.kv_store[k] = v

    def delete(self, keys: List[str]):
        for k in keys:
            del self.kv_store[k]

    def read(self, keys: List[object]) -> Dict:
        records = [self.kv_store[k] for k in keys]
        return records

    def clear(self):
        del self.kv_store
        self.open_connection()

    def key_exist(self, key: object):
        return key in self.kv_store

    def __del__(self):
        self.close_connection()