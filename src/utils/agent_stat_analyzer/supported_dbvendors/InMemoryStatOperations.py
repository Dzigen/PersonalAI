from typing import Union
import numpy as np

from ....db_drivers.table_driver.connectors.InMemoryTableConnector import InMemoryTableConnector
from ..utils import AbstractTableStatOperations


class InMemoryStatOperations(AbstractTableStatOperations):

    def __init__(self, db_conn: InMemoryTableConnector):
        self.db_conn = db_conn

    def calculate_sum(self, column_name: str) -> Union[None, int, float]:
        if len(self.db_conn.table_store) < 1:
            return None

        values = [getattr(item, column_name) for item in self.db_conn.table_store.values() if getattr(item, column_name) is not None]
        return round(sum(values), 3)

    def calculate_min(self, column_name: str) -> Union[None, int, float]:
        if len(self.db_conn.table_store) < 1:
            return None

        values = [getattr(item, column_name) for item in self.db_conn.table_store.values() if getattr(item, column_name) is not None]
        return round(min(values), 3)

    def calculate_max(self, column_name: str) -> Union[None, int, float]:
        if len(self.db_conn.table_store) < 1:
            return None

        values = [getattr(item, column_name) for item in self.db_conn.table_store.values() if getattr(item, column_name) is not None]
        return round(max(values), 3)

    def calculate_std(self, column_name: str) -> Union[None, int, float]:
        if len(self.db_conn.table_store) < 1:
            return None

        values = [getattr(item, column_name) for item in self.db_conn.table_store.values() if getattr(item, column_name) is not None]
        return round(np.std(values), 3)

    def calculate_mean(self, column_name: str) -> Union[None, int, float]:
        if len(self.db_conn.table_store) < 1:
            return None

        values = [getattr(item, column_name) for item in self.db_conn.table_store.values() if getattr(item, column_name) is not None]
        return round(np.mean(values), 3)

    def calculate_median(self, column_name: str) -> Union[None, int, float]:
        if len(self.db_conn.table_store) < 1:
            return None

        values = [getattr(item, column_name) for item in self.db_conn.table_store.values() if getattr(item, column_name) is not None]
        return round(np.median(values), 3)

    def count_notnull_values(self, column_name: str) -> int:
        counter = 0
        for item in self.db_conn.table_store.values():
            if getattr(item, column_name) is not None:
                counter += 1

        return counter

    def count_all_values(self, column_name: str) -> int:
        return self.db_conn.count_items()
