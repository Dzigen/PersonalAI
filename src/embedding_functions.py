from abc import ABC, abstractmethod
import chromadb

# логироавние 
# обработка исключений
# тестирование
# восстановление соединения
 

class EmbeddingDatabaseConnection:
    def __init__(self, some_other_params = None):
        # TODO
        pass
    
    def add_triplets(self, triplets):
        # TODO
        pass
    
    def delete_triplets(self, triplets, deleted_entities):
        # TODO
        pass
    
    def get_node_emb(self, some_other_params = None):
        # TODO
        pass
    
    def get_triplet_emb(self, some_other_params = None):
        # TODO
        pass

class DatabaseInterface(ABC):
    
    @abstractmethod
    def open_connection(self):
        # открытие соединения с бд
        pass

    @abstractmethod
    def close_connection(self):
        # закрытие соединения с бд
        pass

    @abstractmethod
    def create(self):
        # добавить вектора/метаданные/документы/идентификаторы
        pass

    @abstractmethod
    def delete(self):
        # удалить елементы по идентификатору
        pass

    @abstractmethod
    def update(self):
        # обновить документ/метаданные для конкретного семпла
        pass

    @abstractmethod
    def read(self):
        # получить элемент по идентификатору 
        pass

    def __del__(self):
        self.close_connection()


class ChromaConnection(DatabaseInterface):

    def __init__(self) -> None:
        pass
        
    def open_connection(self):
        pass

    def close_connection(self):
        pass

    def create(self):
        pass

    def read(self):
        pass

    def update(self):
        pass

    def delete(self):
        pass

class EmbedderModel:
    def __init__(self) -> None:
        pass

    def encode_query(self):
        pass

    def encode_document(self):
        pass
        