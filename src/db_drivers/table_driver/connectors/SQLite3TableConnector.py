import sqlite3
from typing import List, Dict, Union
from dataclasses import fields, asdict
import os

from .configs import DEFAULT_SQLITE3TABLE_CONFIG
from ..utils import AbstractTableDatabaseConnection, TableDBConnectionConfig, TableDBInstance, BaseTableStucture
from ...utils import restore_connection, retry


class SQLite3TableConnector(AbstractTableDatabaseConnection):

    def __init__(self, config: Union[Dict, TableDBConnectionConfig] = DEFAULT_SQLITE3TABLE_CONFIG) -> None:
        if isinstance(config, dict):
            config: TableDBConnectionConfig = TableDBConnectionConfig.from_dict(config)
        else:
            config.formate_fields()
        self.config = config

    def is_open(self) -> bool:
        # TODO
        raise NotImplementedError

    @retry
    def open_connection(self) -> None:
        if self.config.params.get('database_path', None) is not None:
            os.makedirs(self.config.params['database_path'], exist_ok=True)
        db_path = f"{self.config.params.get('database_path', '.')}/{self.config.db_info['db']}.db"
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

        if self.config.db_info.get('create_table_query', None) is not None:
            self.create_table(self.config.db_info['create_table_query'].format(table_name=self.config.db_info['table']))

    @retry
    def close_connection(self) -> None:
        try:
            self.cursor.close()
            self.conn.close()
        except (TypeError, sqlite3.ProgrammingError) as e:
            pass

    def create_table(self, query: str) -> None:
        self.TABLE_STRUCTURE: Union[None, BaseTableStucture] = self.config.db_info.get('table_info', None)
        self.cursor.execute(query)
        self.conn.commit()

    @restore_connection
    def create(self, items: List[TableDBInstance]) -> None:
        self.validate_items(items)

        column_names = ['id']
        column_names += [field.name for field in fields(self.TABLE_STRUCTURE)]
        ff_items = []
        for item in items:
            if (item.id is None) or (not self.item_exist(item.id)):
                cur_fitem = [item.id]
                values_dict = asdict(item.values)
                cur_fitem += [values_dict[cname] for cname in column_names[1:]]
                ff_items.append(tuple(cur_fitem))

        formated_cnames = ', '.join(column_names)
        placeholders = ', '.join(['?'] * len(column_names))

        # print(formated_cnames, ff_items)

        if len(ff_items) == 1:
            insert_query = f"INSERT INTO {self.config.db_info['table']} ({formated_cnames}) VALUES ({placeholders});"
            self.cursor.execute(insert_query, ff_items[0])
        elif len(ff_items) > 1:
            insert_query_many = f"INSERT INTO {self.config.db_info['table']} ({formated_cnames}) VALUES ({placeholders});"
            self.cursor.executemany(insert_query_many, ff_items)

        self.conn.commit()

    @restore_connection
    def read(self, ids: List[str]) -> List[Union[None, TableDBInstance]]:
        self.validate_ids(ids)

        column_names = ['id']
        column_names += [field.name for field in fields(self.TABLE_STRUCTURE)]
        formated_cnames = ', '.join(column_names)

        placeholders = ', '.join(['?'] * len(ids))
        query = f"SELECT {formated_cnames} FROM {self.config.db_info['table']} WHERE id IN ({placeholders});"

        formated_ids = list(map(lambda id: int(id), ids))
        self.cursor.execute(query, formated_ids)
        rows = self.cursor.fetchall()

        id_positions = {id: i for i, id in enumerate(ids)}
        formated_items = [None] * len(ids)
        # print(formated_items, id_positions)
        for row in rows:
            cur_item = TableDBInstance(
                id=str(row[0]),
                values=self.TABLE_STRUCTURE(
                    **{key: value for key, value in zip(column_names[1:], row[1:])}
                ))
            formated_items[id_positions[cur_item.id]] = cur_item

        return formated_items

    @restore_connection
    def update(self, items: List[TableDBInstance]) -> None:
        # TODO
        raise NotImplementedError

    @restore_connection
    def delete(self, ids: List[str]) -> None:
        self.validate_ids(ids)

        placeholders = ', '.join(['?'] * len(ids))
        query = f"DELETE FROM {self.config.db_info['table']} WHERE id IN ({placeholders});"
        formated_ids = list(map(lambda id: int(id), ids))
        self.cursor.execute(query, formated_ids)
        self.conn.commit()

    @restore_connection
    def count_items(self) -> int:
        query = f"SELECT COUNT(*) FROM {self.config.db_info['table']};"
        self.cursor.execute(query)
        row_count = self.cursor.fetchone()[0]
        return row_count

    @restore_connection
    def item_exist(self, id: str) -> bool:
        self.validate_ids([id])

        formated_id = int(id)
        query = f"SELECT COUNT(*) FROM {self.config.db_info['table']} WHERE id = ?;"
        self.cursor.execute(query, (formated_id,))

        data = self.cursor.fetchone()[0]
        return data > 0

    @restore_connection
    def clear(self) -> None:
        query = f"DELETE FROM {self.config.db_info['table']};"
        self.cursor.execute(query)
        self.conn.commit()
