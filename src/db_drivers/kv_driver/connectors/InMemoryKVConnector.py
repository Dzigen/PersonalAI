from typing import List, Tuple, Dict
import gc
import joblib
import os
import time
import hashlib

from ..utils import KVDBConnectionConfig, AbstractKVDatabaseConnection, KeyValueDBInstance

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

    def is_open(self) -> bool:
        return hasattr(self, 'kv_store')

    def close_connection(self) -> None:
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

    def create(self, items: List[KeyValueDBInstance]) -> None:
        for item in items:
            if item is None or item.id is None or item.value is None:
                raise ValueError

            if type(item.id) is not str or type(item.value) not in [str, float, int]:
                raise ValueError

        unique_ids = set(map(lambda item: item.id, items))
        if len(items) != len(unique_ids):
            raise ValueError

        for item in items:
            if not self.item_exist(item.id):
                self.kv_store[item.id] = item.value

    def read(self, ids: List[str]) -> List[KeyValueDBInstance]:
        for id in ids:
            if (id is None) or (type(id) is not str):
                raise ValueError

        records = [KeyValueDBInstance(id=id, value=self.kv_store[id]) if id in self.kv_store else None for id in ids]
        return records

    def update(self, items: List[KeyValueDBInstance]) -> None:
        # TODO
        pass

    def delete(self, ids: List[str]):
        for id in ids:
            if type(id) is not str:
                raise ValueError

        for id in ids:
            if self.item_exist(id):
                del self.kv_store[id]

    def clear(self):
        del self.kv_store
        gc.collect()
        self.kv_store = dict()

    def count_items(self) -> int:
        return len(self.kv_store)

    def item_exist(self, id: str):
        if type(id) is not str:
            raise ValueError
        return id in self.kv_store
