from typing import List, Dict, Union
import gc
import pickle
import os
import time
import hashlib
from collections import defaultdict

from .configs import DEFAULT_INMEMORYKV_CONFIG
from ..utils import KVDBConnectionConfig, AbstractKVDatabaseConnection, KeyValueDBInstance


class InMemoryKVConnector(AbstractKVDatabaseConnection):

    def __init__(self, config: Union[Dict, KVDBConnectionConfig] = DEFAULT_INMEMORYKV_CONFIG) -> None:
        if isinstance(config, dict):
            config = KVDBConnectionConfig.from_dict(config)
        else:
            config.formate_fields()
        self.config: KVDBConnectionConfig = config

        self.kv_store: Union[None, Dict[str, object]] = None

    def open_connection(self) -> None:
        # print("opening kv connection...")
        if self.config.params['load_from_disk']:
            if self.config.params['load_dump_name'] is None:
                load_path = f"{self.config.params['load_dump_dir']}/{self.config.db_info['db']}/{self.config.db_info['table']}.pkl"
            else:
                load_path = f"{self.config.params['load_dump_dir']}/{self.config.params['load_dump_name']}"
            if os.path.exists(load_path):
                try:
                    with open(load_path, 'rb') as fd:
                        self.kv_store = pickle.load(fd)
                except EOFError:
                    # print(f"The pickle file '{load_path}' is empty or corrupted.")
                    self.kv_store = dict()
            else:
                # print(f"warning: kvstore-dump '{load_path}' doesnt exists. creating empty kv-store")
                os.makedirs(f"{self.config.params['save_dump_dir']}/{self.config.db_info['db']}", exist_ok=True)
                self.kv_store = dict()
        else:
            os.makedirs(f"{self.config.params['save_dump_dir']}/{self.config.db_info['db']}", exist_ok=True)
            self.kv_store = dict()

        if self.config.need_to_clear:
            self.clear()

        # print("kv-store type check: ", type(self.kv_store))
        # print("kv-store is not None:", self.kv_store is not None)

    def is_open(self) -> bool:
        return hasattr(self, 'kv_store')

    def close_connection(self) -> None:
        if self.kv_store is None:
            return
        # print("closing inmemory kv connection...")
        # print("kv-store type check: ", type(self.kv_store))
        # print("kv-store is not None:", self.kv_store is not None)
        if self.config.params['save_on_disk']:
            os.makedirs(self.config.params['save_dump_dir'], exist_ok=True)
            save_path = f"{self.config.params['save_dump_dir']}/{self.config.db_info['db']}/{self.config.db_info['table']}"
            if os.path.exists(save_path) and not self.config.params['rewrite']:
                # print("warning: file on that path is already exists")
                postfix = hashlib.md5(str(time.time()).encode()).hexdigest()
                save_path += f"({postfix})"
            save_path += '.pkl'

            with open(save_path, 'wb') as fd:
                pickle.dump(self.kv_store, fd)

            # print(f"inmemory kv-store saved in: {save_path}")

        self.kv_store = None
        gc.collect()

    def create(self, items: List[KeyValueDBInstance]) -> None:
        for item in items:
            if item is None or item.id is None or item.value is None:
                raise ValueError(f"item: {item}")

            if not isinstance(item.id, str):
                raise ValueError(
                    f"id: t - {type(item.id)}; v - {item.id} value: t - {type(item.value)}; v - {item.value}")

        unique_ids = set(map(lambda item: item.id, items))
        if len(items) != len(unique_ids):
            raise ValueError(f"* len(unique_ids): {len(unique_ids)}\n* items: {items}")

        filtered_items = [
            item for item in items if not self.item_exist(item.id)]

        # находимся в фиксированном размере хранилища
        if self.config.params['max_storage'] > 0:
            n_items_to_delete = (
                self.count_items() + len(filtered_items)) - self.config.params['max_storage']
            if n_items_to_delete > 0:
                self.delete_rare_items(n_items_to_delete)

        for item in filtered_items:
            if isinstance(item.value, bytes):
                dumped_value = pickle.dumps((item.value, 'bytes'))
            else:
                dumped_value = pickle.dumps((item.value, 'notbytes'))

            self.kv_store[item.id] = dumped_value

    def delete_rare_items(self, num: int) -> None:
        # TODO
        pass

    def read(self, ids: List[str]) -> List[KeyValueDBInstance]:
        for id in ids:
            if (id is None) or (not isinstance(id, str)):
                raise ValueError(f"* bad id: {id}\n* ids: {ids}")

        items = []
        item_scores = defaultdict(lambda: 0)
        for id in ids:
            item = None
            if self.item_exist(id):
                loaded_value = pickle.loads(self.kv_store[id])[0]
                item = KeyValueDBInstance(id=id, value=loaded_value)
                item_scores[id] += 1
            items.append(item)

        # Обновляем метрику использования элементов
        self.update_item_scores(item_scores)

        return items

    def update_item_scores(self, mapping: Dict[str, int]) -> None:
        # TODO
        pass

    def update(self, items: List[KeyValueDBInstance]) -> None:
        for item in items:
            if item is None or item.id is None or item.value is None:
                raise ValueError(f"item: {item}")
            if not isinstance(item.id, str) or type(item.value) not in [str, float, int, list, dict, set]:
                raise ValueError(f"item: {item}")
        if len(items) < 1:
            return

        for item in items:
            if self.item_exist(item.id):
                if isinstance(item.value, bytes):
                    dumped_value = pickle.dumps((item.value, 'bytes'))
                else:
                    dumped_value = pickle.dumps((item.value, 'notbytes'))

                self.kv_store[item.id] = dumped_value

    def delete(self, ids: List[str]):
        for id in ids:
            if not isinstance(id, str):
                raise ValueError(f"* bad id: {id}\n* ids: {ids}")

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
        if not isinstance(id, str):
            raise ValueError(f"id: {id}")
        return id in self.kv_store
