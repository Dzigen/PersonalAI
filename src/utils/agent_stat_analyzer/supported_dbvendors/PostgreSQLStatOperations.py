from typing import Union

from ....db_drivers.table_driver.connectors.PostgreSQLTableConnector import PostgreSQLTableConnector
from ..utils import AbstractTableStatOperations


class PostgreSQLStatOperations(AbstractTableStatOperations):

    def __init__(self, db_conn: PostgreSQLTableConnector):
        self.db_conn = db_conn

    def calculate_sum(self, column_name: str) -> Union[None, int, float]:
        query = f"SELECT SUM({column_name}) FROM {self.db_conn.config.db_info['table']};"
        self.db_conn.cursor.execute(query)
        sum_value = self.db_conn.cursor.fetchone()[0]
        return None if sum_value is None else round(float(sum_value), 3)

    def calculate_min(self, column_name: str) -> Union[None, int, float]:
        query = f"SELECT MIN({column_name}) FROM {self.db_conn.config.db_info['table']};"
        self.db_conn.cursor.execute(query)
        min_value = self.db_conn.cursor.fetchone()[0]
        return None if min_value is None else round(min_value, 3)

    def calculate_max(self, column_name: str) -> Union[None, int, float]:
        query = f"SELECT MAX({column_name}) FROM {self.db_conn.config.db_info['table']};"
        self.db_conn.cursor.execute(query)
        max_value = self.db_conn.cursor.fetchone()[0]
        return None if max_value is None else round(max_value, 3)

    def calculate_std(self, column_name: str) -> Union[None, int, float]:
        nnull_values_count = self.count_notnull_values(column_name)
        if nnull_values_count < 1:
            return None

        query = f"SELECT stddev_pop({column_name}) FROM {self.db_conn.config.db_info['table']};"
        self.db_conn.cursor.execute(query)
        std_value = float(self.db_conn.cursor.fetchone()[0])
        return round(std_value, 3)

    def calculate_mean(self, column_name: str) -> Union[None, int, float]:
        query = f"SELECT AVG({column_name}) FROM {self.db_conn.config.db_info['table']};"
        self.db_conn.cursor.execute(query)
        mean_value = self.db_conn.cursor.fetchone()[0]
        return None if mean_value is None else round(float(mean_value), 3)

    def calculate_median(self, column_name: str) -> Union[None, int, float]:
        nnull_values_count = self.count_notnull_values(column_name)
        if nnull_values_count < 1:
            return None

        query = None
        if nnull_values_count % 2 == 1:
            odd_query = f'''
            SELECT {column_name}
            FROM {self.db_conn.config.db_info['table']}
            ORDER BY {column_name}
            LIMIT 1 OFFSET (SELECT COUNT({column_name}) / 2 FROM {self.db_conn.config.db_info['table']});
            '''
            query = odd_query
        else:
            even_query = f'''
            SELECT AVG({column_name})
            FROM (
                SELECT {column_name}
                FROM {self.db_conn.config.db_info['table']}
                ORDER BY {column_name}
                LIMIT 2 - (SELECT COUNT({column_name}) FROM {self.db_conn.config.db_info['table']}) % 2
                OFFSET (SELECT (COUNT({column_name}) - 1) / 2 FROM {self.db_conn.config.db_info['table']})
            );
            '''
            query = even_query

        self.db_conn.cursor.execute(query)
        median_value = float(self.db_conn.cursor.fetchone()[0])
        return round(median_value, 3)

    def count_notnull_values(self, column_name: str) -> int:
        query = f"SELECT COUNT({column_name}) FROM {self.db_conn.config.db_info['table']};"
        self.db_conn.cursor.execute(query)
        nnull_count = self.db_conn.cursor.fetchone()[0]
        return nnull_count

    def count_all_values(self, column_name: str) -> int:
        return self.db_conn.count_items()
