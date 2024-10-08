from typing import List, Tuple, Dict


from .utils import KVDBConnectionConfig, AbstractKVDatabaseConnection

DEFAULT_INMEMORY_CONFIG = KVDBConnectionConfig(host='localhost', port=27017)

class InMemoryConnector(AbstractKVDatabaseConnection):
    
    def __init__(self, config: KVDBConnectionConfig = DEFAULT_INMEMORY_CONFIG) -> None:
        self.config = config

    def open_connection(self):
        # открытие соединения с бд
        pass

    def close_connection(self):
        # закрытие соединения с бд
        pass

    def create(self):
        # добавить вектора/метаданные/документы/идентификаторы
        pass

    def delete(self):
        # удалить елементы по идентификатору
        pass

    def read(self):
        # получить сущность по идентификатору 
        pass

    def clear(self):
        # Удаление содержания заднной базы 
        pass

    def key_exist(self):
        # проверка на существование записи с данным ключом в бд
        pass

    def __del__(self):
        self.close_connection()