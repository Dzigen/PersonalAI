from typing import List, Tuple, Dict
from pymongo import MongoClient

from .utils import KVDBConnectionConfig, AbstractKVDatabaseConnection

DEFAULT_MONGO_CONFIG = KVDBConnectionConfig(
    host='localhost', port=27017, 
    params={'dbname': 'personalai', 'collectionname': 'astar', 
            'user': 'mongo_root', 'password': 'root_password'})

class MongoConnector(AbstractKVDatabaseConnection):
    
    def __init__(self, config: KVDBConnectionConfig = DEFAULT_MONGO_CONFIG) -> None:
        self.config = config
        self.open_connection()

    def open_connection(self):
        connection_url = f"mongodb://{self.config.params['user']}:{self.config.params['password']}@{self.config.host}"
        self.client = MongoClient(connection_url)
        self.collection = self.client[self.config.params['dbname']][self.config.params['collectionname']]

    def close_connection(self):
        self.client.close()

    def create(self, items: List[Dict]):
        self.collection.insert_many(items)

    def delete(self, ids: List[str]):
        self.collection.delete_many({"_id": { "$in": ids}})

    def read(self, ids: List[str]) -> List[Dict]:
        return [item for item in self.collection.find({"_id": { "$in": ids}})]

    def key_exist(self):
        # TODO
        pass

    def clear(self):
        self.collection.delete_many({})