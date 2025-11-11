from typing import List, Dict, Tuple, Union
import os
import pickle
import gc
from time import time
import hashlib

from .configs import DEFAULT_INMEMORYTABLE_CONFIG
from ..utils import AbstractTableDatabaseConnection, TableDBConnectionConfig, TableDBInstance, BaseTableStucture
from ....utils.data_structs import create_id


class InMemoryTableConnector(AbstractTableDatabaseConnection):

    def __init__(self, config: Union[Dict, TableDBConnectionConfig] = DEFAULT_INMEMORYTABLE_CONFIG) -> None:
        if isinstance(config, dict):
            config: TableDBConnectionConfig = TableDBConnectionConfig.from_dict(config)
        else:
            config.formate_fields()
        self.config = config

        self.table_store = None

    def is_open(self) -> bool:
        return hasattr(self, 'table_store')

    def open_connection(self) -> None:
        if self.config.params['load_from_disk']:
            if self.config.params['load_dump_name'] is None:
                load_path = f"{self.config.params['load_dump_dir']}/{self.config.db_info['db']}/{self.config.db_info['table']}"
            else:
                load_path = f"{self.config.params['load_dump_dir']}/{self.config.params['load_dump_name']}"

            if os.path.exists(load_path):
                try:
                    with open(load_path, 'rb') as fd:
                        self.table_store = pickle.load(fd)
                except EOFError:
                    # print(f"The pickle file '{load_path}' is empty or corrupted.")
                    self.create_table()
            else:
                # print(f"warning: tablestore-dump '{load_path}' doesnt exists. creating empty table-store")
                os.makedirs(f"{self.config.params['save_dump_dir']}/{self.config.db_info['db']}", exist_ok=True)
                self.create_table()
        else:
            os.makedirs(f"{self.config.params['save_dump_dir']}/{self.config.db_info['db']}", exist_ok=True)
            self.create_table()

        if self.config.need_to_clear:
            self.clear()

    def close_connection(self) -> None:
        # print("closing inmemory table connection...")
        if self.config.params['save_on_disk']:
            os.makedirs(self.config.params['save_dump_dir'], exist_ok=True)
            save_path = f"{self.config.params['save_dump_dir']}/{self.config.db_info['db']}/{self.config.db_info['table']}"
            if os.path.exists(save_path) and not self.config.params['rewrite']:
                # print("warning: file on that path is already exists")
                postfix = hashlib.md5(str(time.time()).encode()).hexdigest()
                save_path += postfix
            save_path += '.pkl'
            with open(save_path, 'wb') as fd:
                pickle.dump(self.table_store, fd)

            # print(f"inmemory table-store saved in: {save_path}")

        self.table_store = None
        gc.collect()

    def create_table(self) -> None:
        self.TABLE_STRUCTURE: Union[None, BaseTableStucture] = self.config.db_info.get('table_info', None)
        self.table_store: Dict[str, BaseTableStucture] = dict()

    def create(self, items: List[TableDBInstance]) -> None:
        self.validate_items(items)

        for item in items:
            item.id = create_id(str(time())) if item.id is None else item.id
            if not self.item_exist(item.id):
                self.table_store[item.id] = item.values

    def read(self, ids: List[str]) -> List[Union[None, TableDBInstance]]:
        self.validate_ids(ids)

        items = []
        for id in ids:
            values = self.table_store.get(id, None)
            item = None if values is None else TableDBInstance(id=id, values=values)
            items.append(item)
        return items

    def update(self, items: List[TableDBInstance]) -> None:
        # TODO
        raise NotImplementedError

    def delete(self, ids: List[str]) -> None:
        self.validate_ids(ids)

        for id in ids:
            if self.item_exist(id):
                del self.table_store[id]

    def count_items(self) -> int:
        return len(self.table_store)

    def item_exist(self, id: str) -> bool:
        self.validate_ids([id])
        return self.table_store.get(id, None) is not None

    def clear(self) -> None:
        self.table_store: Dict[str, BaseTableStucture] = dict()
        gc.collect()
