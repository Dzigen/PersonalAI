from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from sentence_transformers import SentenceTransformer
from typing import Dict, List, Tuple

# __import__('pysqlite3')
import sys
# sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

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
    path: str
    db_name: str
    params: Dict = field(default_factory=lambda: {})
    db_vendor: str = 'chroma'

@dataclass
class VectorDBInstance:
    id: str = -1
    document: str = None
    embedding: List[float] = None
    metadata: Dict = field(default_factory=lambda: dict())

class ChromaConnection(AbstractDatabaseConnection):
    """_summary_"""
    def __init__(self, config: VectorDBConnectionConfig) -> None:
        self.config = config
        self.open_connection()

    def open_connection(self) -> int:
        self.client = chromadb.PersistentClient(path=self.config.path)
        self.collection = self.client.get_or_create_collection(name=self.config.db_name)

    def close_connection(self):
        del self.collection
        del self.client

    def create(self, instances: List[VectorDBInstance]):
        """Добавление объектов в базу.

        Args:
            instances (List[VectorDBInstance]): Список объектов на добавление
        """
        self.collection.add(
            documents=list(map(lambda inst: inst.document, instances)),
            embeddings=list(map(lambda inst: inst.embedding, instances)),
            metadatas=list(map(lambda inst: inst.metadata, instances)),
            ids=list(map(lambda inst: inst.id, instances)))
 
    def read(self, ids: List[str], includes: List[str] = ['embeddings', 'documents', 'metadatas'], **kwargs) -> List[VectorDBInstance]:
        """Получение объектов из базы по их идентификаторам.

        Args:
            ids (List[str]): Идентификаторы объектов.
            includes (List[str], optional): Список полей, информацию по которым нужно получить для каждого объекта. 
                                            Defaults to ['embeddings', 'documents', 'metadatas'].

        Returns:
            List[VectorDBInstance]: Список объектов с заданными идентификаторами.
        """
        raw_instances = self.collection.get(
            include=includes,
            ids=ids, **kwargs) 
                                            
        formates_instances = []
        for i in range(len(raw_instances['ids'])):
            tmp_inst = {requested_field[:-1]: raw_instances[requested_field][i] 
                        for requested_field in includes}
            formates_instances.append(VectorDBInstance(**tmp_inst))

        return formates_instances

    def update(self):
        # TODO
        pass

    def retrieve(
            self, query_instances: List[VectorDBInstance], n_results: int = 50, 
            include: List[str]  = ['embeddings', 'documents', 'metadatas'], **kwargs) -> List[List[Tuple[float, VectorDBInstance]]]:
        """_summary_

        Args:
            query_instances (List[VectorDBInstance]): _description_
            n_results (int, optional): _description_. Defaults to 50.
            include (List[str], optional): Список полей, информацию по которым нужно получить для каждого объекта. Defaults to ['embeddings', 'documents', 'metadatas'].

        Returns:
            List[List[Tuple[float, VectorDBInstance]]]: Списки объектов из бд, релевантных заданным query-объектам.
        """
        
        raw_retrieved_instances = self.collection.query(
            query_embeddings=[inst.embedding for inst in query_instances],
            include=include + ['distances'], n_results=n_results, **kwargs)

        formated_instances = []
        for i in range(len(query_instances)):
            cur_formated_instances = []
            for j in range(len(raw_retrieved_instances['ids'][i])):
                tmp_inst = {requested_field[:-1]: raw_retrieved_instances[requested_field][i][j] 
                        for requested_field in include}
                cur_distance = raw_retrieved_instances['distance'][i][j]

                cur_formated_instances.append((cur_distance, VectorDBInstance(**tmp_inst)))
            formated_instances.append(cur_formated_instances)
        
        return formated_instances

    def delete(self, ids: List[str], **kwargs):
        """Удаление объектов из базы по их идентификаторам.

        Args:
            ids (List[str]): идентификаторы объектов.
        """
        self.collection.delete(ids=ids, **kwargs)

@dataclass
class EmbedderModelConfig:
    model_name_or_path: str = 'intfloat/multilingual-e5-small'
    # prompts: Dict = field(default_factory=lambda: {"query": "query: ", "passage": "passage: "})
    device: str = 'cuda'
    normalize_embeddings: bool = True

class EmbedderModel:
    def __init__(self, config: EmbedderModelConfig = None) -> None:
        self.config = EmbedderModelConfig() if config is None else config
        self.model = SentenceTransformer(
            config.model_name_or_path, device=config.device,
            # prompts=config.prompts
        )

    def encode_queries(self, queries: List[str], **kwargs) -> List[List[float]]:
        """_summary_

        Args:
            queries (List[str]): _description_

        Returns:
            List[List[float]]: _description_
        """
        return self.model.encode(queries, prompt_name='query', 
                                 normalize_embeddings=self.config.normalize_embeddings, **kwargs)

    def encode_passages(self, passages: List[str], **kwargs) -> List[List[float]]:
        """_summary_

        Args:
            passages (List[str]): _description_

        Returns:
            List[List[float]]: _description_
        """
        return self.model.encode(passages, prompt_name='query',
                                 normalize_embeddings=self.config.normalize_embeddings,
                                 **kwargs)


@dataclass
class EmbeddingsDatabaseConnectionConfig:
    nodes_db_config: VectorDBConnectionConfig
    triplets_db_config: VectorDBConnectionConfig
    embedder_config: EmbedderModelConfig

#
AVAILABLE_VECTODB_CONNECTORS = {
    'chroma': ChromaConnection
}

class EmbeddingsDatabaseConnection:
    def __init__(self, config: EmbeddingsDatabaseConnectionConfig):
        self.vecordbs = {
            'nodes': AVAILABLE_VECTODB_CONNECTORS[config.nodes_db_config.db_vendor](config.nodes_db_config),
            'triplets': AVAILABLE_VECTODB_CONNECTORS[config.nodes_db_config.db_vendor](config.triplets_db_config)}
        self.embedder = EmbedderModel(config.embedder_config)

    def add_triplets(self, triplets_ids: List[str], stringified_triplets: List[str], 
                     nodes_ids: List[str] = None, stringified_nodes: List[str] = None) -> None:
        """_summary_

        Args:
            triplets_ids (List[str]): _description_
            stringified_triplets (List[str]): _description_
            nodes_ids (List[str], optional): _description_. Defaults to None.
            stringified_nodes (List[str], optional): _description_. Defaults to None.
        """
        self.add_instances('triplets', triplets_ids, stringified_triplets)
        if nodes_ids is not None:
            self.add_instances('nodes', nodes_ids, stringified_nodes)

    def delete_triplets(self, triplets_ids: List[str], nodes_ids: List[str] = None) -> None:
        """_summary_

        Args:
            triplets_ids (List[str]): _description_
            nodes_ids (List[str], optional): _description_. Defaults to None.
        """
        self.delete_instances('triplets', triplets_ids)
        if nodes_ids is not None:
            self.delete_instances('nodes', nodes_ids)
    
    def add_instances(self, db_type: str, ids: List[str], stringified_instances: List[str]) -> None:
        """_summary_

        Args:
            db_type (str): _description_
            ids (List[str]): _description_
            stringified_instances (List[str]): _description_
        """
        embs = self.embedder.encode_passages(stringified_instances)
        formated_instances = [VectorDBInstance(id=id, document=doc, embedding=emb) 
                            for id, doc, emb in zip(ids, stringified_instances, embs)]
        self.vecordbs[db_type].create(formated_instances)

    def delete_instances(self, db_type: str, ids: List[str]) -> None:
        """_summary_

        Args:
            db_type (str): _description_
            ids (List[str]): _description_
        """
        self.vecordbs[db_type].delete(ids)

    def get_embbeddings(self, db_type: str, ids: List[str]) -> List[List[float]]:
        """_summary_

        Args:
            db_type (str): _description_
            ids (List[str]): _description_

        Returns:
            List[List[float]]: _description_
        """
        instances = self.vecordbs[db_type].read(ids, includes=['embeddings'])
        embeddings = list(map(lambda inst: inst.embedding,instances))
        return embeddings