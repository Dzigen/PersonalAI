from typing import List, Tuple, Dict
import gc
import joblib
import os
import time
import hashlib

from ..utils import KVDBConnectionConfig, AbstractKVDatabaseConnection

DEFAULT_INMEMORYKV_CONFIG = KVDBConnectionConfig(
    host='localhost', 
    params={
        'kvstore_dump_name': 'inmemory_store', 
        'load_from_disk': False, 'load_dump_dir': '.',
        'save_on_disk': True, 'save_dump_dir': '.'
    })

class InMemoryKVConnector(AbstractKVDatabaseConnection):
    
    def __init__(self, config: KVDBConnectionConfig = DEFAULT_INMEMORYKV_CONFIG) -> None:
        self.config = config
        self.open_connection()

    def open_connection(self) -> None:
        if self.config.params['load_from_disk']:
            load_path = f"{self.config.params['load_dump_dir']}/{self.config.params['kvstore_dump_name']}.dump"
            if os.path.exists(load_path):
                self.kv_store = joblib.load(load_path)
            else:
                print(f"warning: kvstore-dump '{load_path}' doesnt exists. creating empty kv-store")
                self.kv_store = dict()
        else:
            self.kv_store = dict()

    def close_connection(self):
        if self.config.params['save_on_disk']:
            save_path = f"{self.config.params['save_dump_dir']}/{self.config.params['kvstore_dump_name']}"
            if os.path.exists(save_path):
                print("warning: file on that path is already exists")
                postfix = hashlib.md5(str(time.time()).encode()).hexdigest()
                save_path += postfix
            save_path += '.dump'

            joblib.dump(self.kv_store, save_path)
        del self.kv_store
        gc.collect()

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
        gc.collect()
        self.kv_store = dict()

    def key_exist(self, key: object):
        return key in self.kv_store

    def __del__(self):
        self.close_connection()