from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from sentence_transformers import SentenceTransformer
from typing import Dict, List
import chromadb
import enum

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
        # обновить документ/метаданные для конкретной сущности в базе
        pass

    @abstractmethod
    def read(self):
        # получить сущность по идентификатору 
        pass

    def __del__(self):
        self.close_connection()

@dataclass
class ChromaConnectionConfig:
    path: str = '../data/vectorized_nodes_tripletes/densedb'
    collection_name: str = 'testdb'

@dataclass
class VectorDBInstance:
    id: str
    document: str
    embedding: List[float]
    metadata: Dict


class ReturnCode(enum.Enum):
    success = 0
    error = 1

class ChromaConnection(DatabaseInterface):
    def __init__(self, config: ChromaConnectionConfig = ChromaConnectionConfig()) -> None:
        self.config = config
        self.open_connection()

    def open_connection(self) -> int:
        self.client = chromadb.PersistentClient(path=self.config.path)
        self.collection = self.client.get_collection(name=self.config.collection_name)

    def close_connection(self):
        del self.collection
        del self.client

    def create(self, instances: List[VectorDBInstance]) -> int:       
        self.collection.add(
            documents=list(map(lambda inst: inst.document, instances)),
            embeddings=list(map(lambda inst: inst.embedding, instances)),
            metadatas=list(map(lambda inst: inst.metadata, instances)),
            ids=list(map(lambda inst: inst.id, instances)))
        return ReturnCode.success
 
    def read(self, ids: List[str], **kwargs) -> List[VectorDBInstance]:
        raw_instances = self.collection.get(
            include=['embeddings', 'documents', 'metadatas'],
            ids=ids, **kwargs) 
                                            
        formates_instances = []
        for i in range(raw_instances['ids']):
            cur_inst =VectorDBInstance(id=raw_instances['ids'][i],
                             document=raw_instances['documents'][i],
                             embedding=raw_instances['embeddins'][i],
                             metadata=raw_instances['metadatas'][i],)
            formates_instances.append(cur_inst)

        return formates_instances

    def update(self):
        # TODO
        pass

    def delete(self, ids: List[str], **kwargs) -> int:
        self.collection.delete(ids=ids, **kwargs)
        return ReturnCode.success

@dataclass
class EmbedderConfig:
    model_name_or_path: str = '../models/intfloat/multilingual-e5-small'
    prompts: Dict = field(default_factory=lambda:{"query": "query: ", "passage": "passage: "})
    device: str = 'cuda'
    normalize_embeddings: bool = True

class EmbedderModel:
    def __init__(self, config: EmbedderConfig = EmbedderConfig()) -> None:
        self.conif = config
        self.model = SentenceTransformer(
            config.model_name_or_path, device=config.device,
            prompts=config.prompts)

    def encode_queries(self, queries: List[str], **kwargs) -> List[List[float]]:
        return self.model.encode(queries, prompt_name='query', 
                                 normalize_embeddings=self.conif.normalize_embeddings, **kwargs)

    def encode_passages(self, passages: List[str], **kwargs) -> List[List[float]]:
        return self.model.encode(passages, prompt_name='query',
                                 normalize_embeddings=self.conif.normalize_embeddings,
                                 **kwargs)
        