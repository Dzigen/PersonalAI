from time import sleep

from typing import List, Dict, Union
from .utils import AbstractVectorDatabaseComposer, AbstractVectorDatabaseConnection, VectorDBInstance
from .VectorDriver import VectorDriverConfig, VectorDriver
from .embedders import EmbedderModel


class VectorComposer(AbstractVectorDatabaseComposer):

    def __init__(self, vdb_config_mapping: Dict[str, VectorDriverConfig], embedders_mapping: Dict[str, EmbedderModel] = dict()) -> None:
        self.vdb_config_mapping = vdb_config_mapping
        self.vdb_conn_mapping: Dict[str, AbstractVectorDatabaseConnection] = dict()
        self.open_connection(embedders_mapping)

    def is_open(self):
        db_info = dict()
        for db_name, db_conn in self.vdb_conn_mapping.items():
            db_info[db_name] = db_conn.is_open()
        return db_info

    def open_connection(self, embedders_mapping: Dict[str, EmbedderModel] = dict()) -> None:
        for db_name, db_config in self.vdb_config_mapping.items():
            self.vdb_conn_mapping[db_name] = VectorDriver.connect(db_config, embedders_mapping.get(db_name, None))

    def check_consistency(self) -> bool:
        sizes_info = self.count_items()
        unique_values = set(list(sizes_info.values()))
        if len(unique_values) > 1:
            raise AssertionError

        return True

    def close_connection(self) -> None:
        for db_conn in self.vdb_conn_mapping.values():
            db_conn.close_connection()

    def create(self, items: List[VectorDBInstance], check_consistency: bool = False) -> None:
        for db_conn in self.vdb_conn_mapping.values():
            db_conn.create(items)
        sleep(1)

        if check_consistency:
            self.check_consistency()

    def read(self, ids: List[str], vdb_name: Union[None, str] = None, includes: List[str] = ['documents', 'metadatas']) -> List[VectorDBInstance]:
        if vdb_name is None:
            vdb_name = list(self.vdb_conn_mapping.keys())[0]
        return self.vdb_conn_mapping[vdb_name].read(ids, includes)

    def update(self) -> None:
        raise NotImplementedError

    def upsert(self, items: List[VectorDBInstance], check_consistency: bool = False) -> None:
        for db_conn in self.vdb_conn_mapping.values():
            db_conn.upsert(items)

        if check_consistency:
            self.check_consistency()

    def delete(self, ids: List[str], check_consistency: bool = False) -> None:
        for db_conn in self.vdb_conn_mapping.values():
            db_conn.delete(ids)

        if check_consistency:
            self.check_consistency()

    def count_items(self) -> Dict[str, int]:
        db_sizes = dict()
        for db_name, db_conn in self.vdb_conn_mapping.items():
            db_sizes[db_name] = db_conn.count_items()
        return db_sizes

    def item_exist(self, id: str) -> bool:
        output = True
        exist_stat = []
        for db_conn in self.vdb_conn_mapping.values():
            is_exist = db_conn.item_exist(id)
            exist_stat.append(is_exist)
            output &= is_exist

        # проверка компоновщика на консистентность
        unique_values = set(exist_stat)
        if len(unique_values) > 1:
            raise AssertionError

        return output

    def clear(self, check_consistency: bool = False) -> None:
        for db_conn in self.vdb_conn_mapping.values():
            db_conn.clear()
        sleep(1)

        if check_consistency:
            self.check_consistency()
