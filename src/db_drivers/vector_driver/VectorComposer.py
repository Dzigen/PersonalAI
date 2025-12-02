from time import sleep

from typing import List, Dict, Union
from .utils import AbstractVectorDatabaseComposer, AbstractVectorDatabaseConnection, VectorDBInstance
from .VectorDriver import VectorDriverConfig, VectorDriver
from .embedders import EmbedderModel


class VectorComposer(AbstractVectorDatabaseComposer):
    """Компоновщик нескольких векторных хранилищ.

    Оборачивает несколько экземпляров AbstractVectorDatabaseConnection и обеспечивает:
     - единую точку входа для операций upsert/read/delete;
     - опциональную проверку консистентности данных.

    :param vdb_config_mapping: Сопоставление имени хранилища и его конфигурации.
    :type vdb_config_mapping: Dict[str, Union[Dict, VectorDriverConfig]]
    :param embedders_mapping: Сопоставление имени хранилища и экземпляра EmbedderModel, который будет использоваться при подключении.
    :type embedders_mapping: Dict[str, EmbedderModel]
    """
    def __init__(self, vdb_config_mapping: Dict[str, Union[Dict, VectorDriverConfig]], embedders_mapping: Dict[str, EmbedderModel] = dict()) -> None:
        for vdb_name, vdb_config in vdb_config_mapping.items():
            if isinstance(vdb_config, dict):
                vdb_config_mapping[vdb_name] = VectorDriverConfig.from_dict(vdb_config)
            else:
                vdb_config_mapping[vdb_name].formate_fields()
        self.vdb_config_mapping: Dict[str, VectorDriverConfig] = vdb_config_mapping

        self.vdb_conn_mapping: Dict[str, AbstractVectorDatabaseConnection] = dict()

        self.open_connection(embedders_mapping)

    def is_open(self):
        db_info = dict()
        for db_name, db_conn in self.vdb_conn_mapping.items():
            db_info[db_name] = db_conn.is_open()
        return db_info

    def open_connection(self, embedders_mapping: Dict[str, EmbedderModel] = dict()) -> None:
        """Метод предназначен для открытия соединений со всеми сконфигурированными векторными хранилищами.

        :param embedders_mapping: Сопоставление имени хранилища и эмбеддера, который должен быть передан в конкретный коннектор.
        :type embedders_mapping: Dict[str, EmbedderModel]
        """
        for db_name, db_config in self.vdb_config_mapping.items():
            self.vdb_conn_mapping[db_name] = VectorDriver.connect(db_config, embedders_mapping.get(db_name, None))

    def check_consistency(self) -> bool:
        sizes_info = self.count_items()
        unique_values = set(list(sizes_info.values()))
        if len(unique_values) > 1:
            raise AssertionError(f"vcomposer-db sizes: {sizes_info}")

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
        """Метод предназначен для чтения объектов по их идентификаторам из одного из хранилищ.

        :param ids: Список идентификаторов объектов.
        :type ids: List[str]
        :param vdb_name: Имя векторного хранилища. Если None, используется первое доступное подключение.
        :type vdb_name: Union[None, str]
        :param includes: Список полей, которые необходимо вернуть.
        :type includes: List[str]
        :return: Список найденных объектов в формате VectorDBInstance.
        :rtype: List[VectorDBInstance]
        """
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
        """Метод предназначен для получения статистики по каждому из подключенных хранилищ.

        :return: Словарь {имя_хранилища: количество_элементов}.
        :rtype: Dict[str, int]
        """
        db_sizes = dict()
        for db_name, db_conn in self.vdb_conn_mapping.items():
            db_sizes[db_name] = db_conn.count_items()
        return db_sizes

    def item_exist(self, id: str) -> bool:
        """Метод предназначен для проверки существования объекта в каждом из хранилищ.

        :param id: Идентификатор объекта.
        :type id: str
        :return: True, если объект существует во всех хранилищах; False при отсутствии хотя бы в одном.
        :rtype: bool
        """
        output = True
        exist_stat = []
        for db_conn in self.vdb_conn_mapping.values():
            is_exist = db_conn.item_exist(id)
            exist_stat.append(is_exist)
            output &= is_exist

        # проверка компоновщика на консистентность
        # unique_values = set(exist_stat)
        # if len(unique_values) > 1:
        #     raise AssertionError

        return output

    def clear(self, check_consistency: bool = False) -> None:
        """Метод предназначен для очистки всех подключённых векторных хранилищ.

        :param check_consistency: Если True, после очистки будет выполнена проверка консистентности (ожидается, что все хранилища пусты).
        :type check_consistency: bool
        """
        for db_conn in self.vdb_conn_mapping.values():
            db_conn.clear()
        sleep(1)

        if check_consistency:
            self.check_consistency()

    def __del__(self):
        for v_conn in self.vdb_conn_mapping.values():
            try:
                v_conn.close_connection()
            except AttributeError:
                pass
