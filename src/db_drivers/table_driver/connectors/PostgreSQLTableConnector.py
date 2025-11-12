import psycopg2
from typing import List, Dict, Tuple, Union
from dataclasses import fields, asdict
from collections import defaultdict

from .configs import DEFAULT_POSTGRESQLTABLE_CONFIG
from ..utils import AbstractTableDatabaseConnection, TableDBConnectionConfig, TableDBInstance, BaseTableStucture


class PostgreSQLTableConnector(AbstractTableDatabaseConnection):

    def __init__(self, config: Union[Dict, TableDBConnectionConfig] = DEFAULT_POSTGRESQLTABLE_CONFIG) -> None:
        if isinstance(config, dict):
            config: TableDBConnectionConfig = TableDBConnectionConfig.from_dict(config)
        else:
            config.formate_fields()
        self.config = config

    def is_open(self) -> bool:
        # TODO
        raise NotImplementedError

    def open_connection(self) -> None:
        self.conn = psycopg2.connect(
            host=self.config.host,
            database=self.config.db_info['db'],
            user=self.config.params['username'],
            password=self.config.params['password'],
            port=self.config.port
        )
        self.cursor = self.conn.cursor()

        if self.config.db_info.get('create_table_query', None) is not None:
            self.create_table(self.config.db_info['create_table_query'].format(table_name=self.config.db_info['table']))

    def close_connection(self) -> None:
        try:
            self.cursor.close()
            self.conn.close()
        except TypeError:
            pass

    def create_table(self, query: str) -> None:
        self.TABLE_STRUCTURE: Union[None, BaseTableStucture] = self.config.db_info.get('table_info', None)
        self.cursor.execute(query)
        self.conn.commit()

    def create(self, items: List[TableDBInstance]) -> None:
        self.validate_items(items)

        ff_items_groups: Dict[Tuple, List[Tuple]] = defaultdict(list)
        for item in items:
            if (item.id is None) or (not self.item_exist(item.id)):
                values_dict = asdict(item.values)
                values_dict['id'] = item.id

                nnull_cnames, nnull_fitem = [], []
                for k, v in values_dict.items():
                    if v is not None:
                        nnull_cnames.append(k)
                        nnull_fitem.append(v)

                ff_items_groups[tuple(nnull_cnames)].append(tuple(nnull_fitem))

        for column_names, items_group in ff_items_groups.items():
            formated_cnames = ', '.join(column_names)
            placeholders = ', '.join(['%s'] * len(column_names))

            # print(formated_cnames, items_group)

            if len(items_group) == 1:
                insert_query = f"INSERT INTO {self.config.db_info['table']} ({formated_cnames}) VALUES ({placeholders});"
                self.cursor.execute(insert_query, items_group[0])
            elif len(items_group) > 1:
                insert_query_many = f"INSERT INTO {self.config.db_info['table']} ({formated_cnames}) VALUES ({placeholders});"
                self.cursor.executemany(insert_query_many, items_group)

            self.conn.commit()

    def read(self, ids: List[str]) -> List[Union[None, TableDBInstance]]:
        self.validate_ids(ids)

        if len(ids) < 1:
            return list()

        column_names = ['id']
        column_names += [field.name for field in fields(self.TABLE_STRUCTURE)]
        formated_cnames = ', '.join(column_names)

        query = f"SELECT {formated_cnames} FROM {self.config.db_info['table']} WHERE id IN %s;"

        formated_ids = tuple(map(lambda id: int(id), ids))
        self.cursor.execute(query, (formated_ids, ))
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

    def update(self, items: List[TableDBInstance]) -> None:
        # TODO
        raise NotImplementedError

    def delete(self, ids: List[str]) -> None:
        self.validate_ids(ids)

        if len(ids) < 1:
            return

        query = f"DELETE FROM {self.config.db_info['table']} WHERE id IN %s;"
        formated_ids = tuple(map(lambda id: int(id), ids))
        self.cursor.execute(query, (formated_ids,))
        self.conn.commit()

    def count_items(self) -> int:
        query = f"SELECT COUNT(*) FROM {self.config.db_info['table']};"
        self.cursor.execute(query)
        row_count = self.cursor.fetchone()[0]
        return row_count

    def item_exist(self, id: str) -> bool:
        self.validate_ids([id])

        formated_id = int(id)
        query = f"SELECT COUNT(*) FROM {self.config.db_info['table']} WHERE id = %s;"
        self.cursor.execute(query, (formated_id,))

        data = self.cursor.fetchone()[0]
        return data > 0

    def clear(self) -> None:
        query = f"DELETE FROM {self.config.db_info['table']};"
        self.cursor.execute(query)
        self.conn.commit()
