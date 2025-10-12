from typing import Union
import numpy as np

from ....db_drivers.table_driver.connectors.MongoTableConnector import MongoTableConnector
from ..utils import AbstractTableStatOperations


class MongoStatOperations(AbstractTableStatOperations):

    def __init__(self, db_conn: MongoTableConnector):
        self.db_conn = db_conn

    def calculate_sum(self, column_name: str) -> Union[None, int, float]:
        raw_value = list(self.db_conn._collection.aggregate([
            {'$group': {'_id': None, 'sum': {'$sum': f"${column_name}"}}}
        ]))
        return None if len(raw_value) < 1 else round(float(raw_value[0]['sum']), 3)

    def calculate_min(self, column_name: str) -> Union[None, int, float]:
        raw_value = list(self.db_conn._collection.aggregate([
            {'$group': {'_id': None, 'min': {'$min': f"${column_name}"}}}
        ]))
        return None if len(raw_value) < 1 else round(float(raw_value[0]['min']), 3)

    def calculate_max(self, column_name: str) -> Union[None, int, float]:
        raw_value = list(self.db_conn._collection.aggregate([
            {'$group': {'_id': None, 'max': {'$max': f"${column_name}"}}}
        ]))
        return None if len(raw_value) < 1 else round(float(raw_value[0]['max']), 3)

    def calculate_std(self, column_name: str) -> Union[None, int, float]:
        raw_value = list(self.db_conn._collection.aggregate([
            {'$group': {'_id': None, 'std': {'$stdDevPop': f"${column_name}"}}}
        ]))
        return None if len(raw_value) < 1 else round(float(raw_value[0]['std']), 3)

    def calculate_mean(self, column_name: str) -> Union[None, int, float]:
        raw_value = list(self.db_conn._collection.aggregate([
            {'$group': {'_id': None, 'avg': {'$avg': f"${column_name}"}}}
        ]))
        return None if len(raw_value) < 1 else round(float(raw_value[0]['avg']), 3)

    def calculate_median(self, column_name: str) -> Union[None, int, float]:
        nnull_values_count = self.count_notnull_values(column_name)
        if nnull_values_count < 1:
            return None

        median_value = None
        if nnull_values_count % 2 == 1:
            raw_value = list(self.db_conn._collection.aggregate([
                {'$group': {'_id': None, 'median': {'$median': {'input': f"${column_name}", 'method': 'approximate'}}}}
            ]))
            if len(raw_value) > 0:
                median_value = round(float(raw_value[0]['median']), 3)
        else:
            count = self.db_conn._collection.count_documents({})
            raw_value1 = list(self.db_conn._collection.find().sort(
                {column_name: 1}).skip(int((count - 1) / 2)).limit(1))[0]
            raw_value2 = list(self.db_conn._collection.find().sort(
                {column_name: 1}).skip(int(count / 2)).limit(1))[0]

            median_value = round(np.mean([raw_value1[column_name], raw_value2[column_name]]), 3)

        return median_value

    def count_notnull_values(self, column_name: str) -> int:
        return self.db_conn._collection.count_documents({column_name: {"$ne": None}})

    def count_all_values(self, column_name: str) -> int:
        return self.db_conn.count_items()
