from typing import List, Tuple, Dict
from pymongo import MongoClient

from ..utils import KVDBConnectionConfig, AbstractKVDatabaseConnection, KeyValueDBInstance

DEFAULT_MONGO_CONFIG = KVDBConnectionConfig(
    host='localhost', port=27017,
    db_info={'dbname': 'personalai', 'collection': 'astar_ip'},
    params={'user': 'mongo_root', 'password': 'root_password'})

# TODO
class MongoConnector(AbstractKVDatabaseConnection):

    def __init__(self, config: KVDBConnectionConfig = DEFAULT_MONGO_CONFIG) -> None:
        self.config = config
        self.open_connection()

    def open_connection(self):
        connection_url = f"mongodb://{self.config.params['user']}:{self.config.params['password']}@{self.config.host}"
        self.client = MongoClient(connection_url)
        self.collection = self.client[self.config.params['dbname']][self.config.params['collectionname']]

    def is_open(self) -> bool:
        # TODO
        pass

    def close_connection(self):
        self.client.close()

    def create(self, items: List[KeyValueDBInstance]) -> None:
        self.collection.insert_many(items)

    def delete(self, ids: List[str]) -> None:
        self.collection.delete_many({"_id": { "$in": ids}})

    def read(self, ids: List[str]) -> List[Dict]:
        return [item for item in self.collection.find({"_id": { "$in": ids}})]

    def item_exist(self, id: str) -> bool:
        # TODO
        pass

    def count_items(self) -> int:
        # TODO
        pass

    def clear(self):
        self.collection.delete_many({})
