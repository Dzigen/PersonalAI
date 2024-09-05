from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from sentence_transformers import SentenceTransformer
from typing import Dict, List
import chromadb
import enum

class AbstractDatabaseConnection(ABC):
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

    @abstractmethod
    def retrieve(self):
        # извлечение N ближайших сущностей к данной по заданной метрике
        pass

    def __del__(self):
        self.close_connection()

@dataclass
class VectorDBConnectionConfig:
    db_name: str = 'testdb'
    path: str
    params: Dict

@dataclass
class VectorDBInstance:
    id: str
    document: str = None
    embedding: List[float] = None
    metadata: Dict = field(default=lambda: dict())


class ReturnCode(enum.Enum):
    success = 0
    error = 1

class ChromaConnection(AbstractDatabaseConnection):
    def __init__(self, config: VectorDBConnectionConfig) -> None:
        self.config = config
        self.open_connection()

    def open_connection(self) -> int:
        self.client = chromadb.PersistentClient(path=self.config.path)
        self.collection = self.client.get_collection(name=self.config.collection_name)

    def close_connection(self):
        del self.collection
        del self.client

    def create(self, instances: List[VectorDBInstance]):       
        self.collection.add(
            documents=list(map(lambda inst: inst.document, instances)),
            embeddings=list(map(lambda inst: inst.embedding, instances)),
            metadatas=list(map(lambda inst: inst.metadata, instances)),
            ids=list(map(lambda inst: inst.id, instances)))
 
    def read(self, ids: List[str], includes: List[str] = ['embeddings', 'documents', 'metadatas'], **kwargs) -> List[VectorDBInstance]:
        raw_instances = self.collection.get(
            include=includes + ['ids'],
            ids=ids, **kwargs) 
                                            
        formates_instances = []
        for i in range(raw_instances['ids']):
            tmp_inst = {requested_field[:-1]: raw_instances[requested_field][i] 
                        for requested_field in includes}
            formates_instances.append(VectorDBInstance(**tmp_inst))

        return formates_instances

    def update(self):
        # TODO
        pass

    def retrieve(
            self, query_instances: VectorDBInstance, n_results: int = 50, 
            includes: List[str]  = ['embeddings', 'documents', 'metadatas']) -> List[List[VectorDBInstance]]:
        
        raw_retrieved_instances = self.collection.query(
            query_embeddings=[inst.embedding for inst in query_instances],
            include=includes + ['ids'], n_results=n_results)

        formated_instances = []
        for i in range(len(query_instances)):
            cur_formated_instances = []
            for j in range(len(raw_retrieved_instances['ids'][i])):
                tmp_inst = {requested_field[:-1]: raw_retrieved_instances[requested_field][i][j] 
                        for requested_field in includes}
                cur_formated_instances.append(VectorDBInstance(**tmp_inst))
            formated_instances.append(cur_formated_instances)
        
        return formated_instances

    def delete(self, ids: List[str], **kwargs):
        self.collection.delete(ids=ids, **kwargs)

@dataclass
class EmbedderModelConfig:
    model_name_or_path: str = '../models/intfloat/multilingual-e5-small'
    prompts: Dict = field(default_factory=lambda:{"query": "query: ", "passage": "passage: "})
    device: str = 'cuda'
    normalize_embeddings: bool = True

class EmbedderModel:
    def __init__(self, config: EmbedderModelConfig = None) -> None:
        self.config = EmbedderModelConfig() if config is None else config
        self.model = SentenceTransformer(
            config.model_name_or_path, device=config.device,
            prompts=config.prompts)

    def encode_queries(self, queries: List[str], **kwargs) -> List[List[float]]:
        return self.model.encode(queries, prompt_name='query', 
                                 normalize_embeddings=self.config.normalize_embeddings, **kwargs)

    def encode_passages(self, passages: List[str], **kwargs) -> List[List[float]]:
        return self.model.encode(passages, prompt_name='query',
                                 normalize_embeddings=self.config.normalize_embeddings,
                                 **kwargs)


@dataclass
class EmbedderDatabaseConnectionConfig:
    db_vendor: str = 'chroma'
    node_db_config: VectorDBConnectionConfig
    triplets_db_config: VectorDBConnectionConfig
    embedder_config: EmbedderModelConfig

AVAILABLE_VECTODB_CONNECTORS = {
    'chroma': ChromaConnection
}

class EmbeddingDatabaseConnection:
    def __init__(self, config: EmbedderDatabaseConnectionConfig):
        self.vecordbs = {
            'nodes': AVAILABLE_VECTODB_CONNECTORS[config.db_vendor](config.node_db_config),
            'triplets': AVAILABLE_VECTODB_CONNECTORS[config.db_vendor](config.triplets_db_config)}
        self.embedder = EmbedderModel(config.embedder_config)

    def add_triplets(self, triplets_ids: List[str], stringified_triplets: List[str], 
                     nodes_ids: List[str] = None, stringified_nodes: List[str] = None):
        self.add_instances('triplets', triplets_ids, stringified_triplets)
        if nodes_ids is not None:
            self.add_instances('nodes', nodes_ids, stringified_nodes)

    def delete_triplets(self, triplets_ids: List[str], nodes_ids: List[str] = None):
        self.delete_instances('triplets', triplets_ids)
        if nodes_ids is not None:
            self.delete_instances('nodes', nodes_ids)
    
    def add_instances(self, db_type: str, ids: List[str], stringified_instances: List[str]):
        embs = self.embedder.encode_passages(stringified_instances)
        formated_instances = [VectorDBInstance(id=id, document=doc, embedding=emb) 
                            for id, doc, emb in zip(ids, stringified_instances, embs)]
        self.vecordbs[db_type].create(formated_instances)

    def delete_instances(self, db_type: str, ids: List[str]):
        self.vecordbs[db_type].delete(ids)

    def get_embbeddings(self, ids: List[str]) -> List[List[float]]:
        instances = self.db.read(ids, includes=['embeddins'])
        embeddings = list(map(lambda inst: inst.embedding,instances))
        return embeddings