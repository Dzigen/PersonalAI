import pymongo
from typing import List, Dict, Tuple, Union
from dataclasses import asdict
from time import time

from .configs import DEFAULT_MONGOTABLE_CONFIG
from ..utils import AbstractTableDatabaseConnection, TableDBConnectionConfig, TableDBInstance, BaseTableStucture
from ....utils.data_structs import create_id


class MongoTableConnector(AbstractTableDatabaseConnection):

    def __init__(self, config: Union[Dict, TableDBConnectionConfig] = DEFAULT_MONGOTABLE_CONFIG) -> None:
        if isinstance(config, dict):
            config: TableDBConnectionConfig = TableDBConnectionConfig.from_dict(config)
        else:
            config.formate_fields()
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
        self.create_table()

        if self.config.need_to_clear:
            self.clear()

    def close_connection(self) -> None:
        self._client.close()

    def create_table(self) -> None:
        self.TABLE_STRUCTURE: Union[None, BaseTableStucture] = self.config.db_info.get('table_info', None)
        self._collection = self._client[self.config.db_info['db']][self.config.db_info['table']]

    def create(self, items: List[TableDBInstance]) -> None:
        self.validate_items(items)

        formated_items: List[Dict[str, object]] = list()
        for item in items:
            item.id = create_id(str(time())) if item.id is None else item.id
            if not self.item_exist(item.id):
                fitem = asdict(item.values)
                fitem['_id'] = item.id
                formated_items.append(fitem)

        if len(formated_items) > 0:
            self._collection.insert_many(formated_items)

    def read(self, ids: List[str]) -> List[Union[None, TableDBInstance]]:
        self.validate_ids(ids)

        if len(ids) < 1:
            return []

        items = self._collection.find({"_id": {"$in": ids}})

        id_positions = {id: i for i, id in enumerate(ids)}
        formated_items = [None] * len(ids)
        # print(formated_items, id_positions)
        for item in items:
            cur_item = TableDBInstance(
                id=item['_id'],
                values=self.TABLE_STRUCTURE(
                    **{key: value for key, value in item.items() if key != '_id'}
                ))
            formated_items[id_positions[cur_item.id]] = cur_item

        return formated_items

    def update(self, items: List[TableDBInstance]) -> None:
        # TODO
        raise NotImplementedError

    def delete(self, ids: List[str]) -> None:
        self.validate_ids(ids)

        if len(ids) > 0:
            self._collection.delete_many({'_id': {"$in": ids}})

    def count_items(self) -> int:
        return self._collection.count_documents({})

    def item_exist(self, id: str) -> bool:
        self.validate_ids([id])

        item = self._collection.find_one({'_id': id})
        return item is not None

    def clear(self) -> None:
        self._collection.drop()
