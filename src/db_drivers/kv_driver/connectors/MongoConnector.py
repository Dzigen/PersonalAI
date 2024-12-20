import pymongo
from typing import List, Tuple, Dict

from src.db_drivers.kv_driver.utils import AbstractKVDatabaseConnection, KVDBConnectionConfig, KeyValueDBInstance

DEFAULT_MONGOKV_CONFIG = KVDBConnectionConfig(host='localhost', port=27017,
                                              db_info={'db': 'test_db', 'table': 'test_collection'},
                                              params={'username': 'user', 'password': 'pass', 'max_storage': -1})

class MongoKVConnector(AbstractKVDatabaseConnection):

    def __init__(self, config: KVDBConnectionConfig = DEFAULT_MONGOKV_CONFIG) -> None:
        self.config = config

    def is_open(self) -> bool:
        try:
            self._client.server_info()
            return True
        except pymongo.errors.ServerSelectionTimeoutError as err:
            print(str(err))
            return False

    def open_connection(self) -> None:
        self._client = pymongo.MongoClient(f'mongodb://{self.config.host}:{self.config.port}',
                                           username=self.config.params['username'], password=self.config.params['password'])
        self._collection = self._client[self.config.db_info['db']][self.config.db_info['table']]

        if self.config.need_to_clear:
            self.clear()

    def close_connection(self) -> None:
        self._client.close()

    def create(self, items: List[KeyValueDBInstance]) -> None:
        filtered_items = [{'_id': item.id, 'value': item.value}
                          for item in items if self._collection.find_one({'_id': item.id}) is None]

        # TODO
        # фиксировать максимальный размер хранилища

        if len(filtered_items) > 0:
            self._collection.insert_many(filtered_items)

    def read(self, ids: List[str]) -> List[KeyValueDBInstance]:
        if len(ids) < 1:
            return []
        items = self._collection.find({"_id": {"$in": ids}})
        items_dict = {item['_id']: item for item in items}

        sorted_items = []
        for id in ids:
            item = items_dict.get(id, None)
            if item is not None:
                item = KeyValueDBInstance(id=item['_id'], value=item['value'])

            sorted_items.append(item)

        return sorted_items

    def update(self, items: List[KeyValueDBInstance]) -> None:
        if len(items) < 1:
            return

        existig_items = self._collection.find({"_id": {"$in": [item.id for item in items]}})

        items_dict = {item.id: item for item in items}
        filtered_items = [items_dict[item['_id']] for item in existig_items if items_dict[item['_id']] is not None]

        for item in filtered_items:
            self._collection.update_one({'_id': item.id}, {"$set": { "value": item.value}})

    def delete(self, ids: List[str]) -> None:
        if len(ids) > 0:
            self._collection.delete_many({'_id': {"$in": ids}})

    def count_items(self) -> int:
        return self._collection.count_documents({})

    def item_exist(self, id: str) -> bool:
        item = self._collection.find_one({'_id': id})
        return item is not None

    def clear(self) -> None:
        self._collection.drop()
