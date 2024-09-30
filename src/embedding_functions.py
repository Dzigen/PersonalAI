from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from sentence_transformers import SentenceTransformer
from typing import Dict, List, Tuple, Union
import chromadb
import math

from .utils.data_structs import Triplet, Relation, Node, TripletCreator, NodeCreator


@dataclass
class Node:
    id: str
    name: str
    type: str
    prop: dict

@dataclass
class Relation:
    id: str
    name: str
    type: str
    prop: dict

@dataclass
class Triplet:
    start_node: Node 
    relation: Relation 
    end_node: Node
    
class ContextType(Enum):
    simple = "simple"
    hyper = "hyper"
    episodic = "episodic"

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

    @abstractmethod
    def clear(self):
        # Удаление содержания заднной базы 
        pass

    def __del__(self):
        self.close_connection()

@dataclass
class VectorDBConnectionConfig:
    path: str
    db_name: str
    params: Dict = field(default_factory=lambda: {"hnsw:space": "ip"})
    db_vendor: str = 'chroma'
    need_to_clear: bool = False
    is_exist: bool = True

@dataclass
class VectorDBInstance:
    id: str = None
    document: str = None
    embedding: List[float] = None
    metadata: Dict = field(default_factory=lambda: dict())

class ChromaConnection(AbstractDatabaseConnection):
    def __init__(self, config: VectorDBConnectionConfig) -> None:
        self.config = config
        self.open_connection()

    def open_connection(self):
        self.client = chromadb.PersistentClient(path=self.config.path)

        if self.config.is_exist:
            if self.config.need_to_clear:
                self.clear()
            else:
                self.collection = self.client.get_collection(name=self.config.db_name) 
            
        else:
            self.collection = self.client.create_collection(name=self.config.db_name, 
                                                            metadata=self.config.params)

    def close_connection(self):
        del self.collection
        del self.client

    def clear(self):
        self.client.delete_collection(name=self.config.db_name)
        self.collection = self.client.create_collection(name=self.config.db_name, 
                                                        metadata=self.config.params)

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
                        for requested_field in includes + ['ids']}
            formates_instances.append(VectorDBInstance(**tmp_inst))

        return formates_instances

    def update(self):
        # TODO
        pass

    def retrieve(
            self, query_instances: List[VectorDBInstance], n_results: int = 50, 
            includes: List[str]  = ['embeddings', 'documents', 'metadatas'], **kwargs) -> List[List[Tuple[float, VectorDBInstance]]]:
        """_summary_

        Args:
            query_instances (List[VectorDBInstance]): _description_
            n_results (int, optional): _description_. Defaults to 50.
            includes (List[str], optional): Список полей, информацию по которым нужно получить для каждого объекта. Defaults to ['embeddings', 'documents', 'metadatas'].

        Returns:
            List[List[Tuple[float, VectorDBInstance]]]: Списки объектов из бд, релевантных заданным query-объектам.
        """

        raw_retrieved_instances = self.collection.query(
            query_embeddings=[inst.embedding.tolist() for inst in query_instances],
            include=includes + ['distances'], n_results=n_results, **kwargs)

        formated_instances = []
        for i in range(len(query_instances)):
            cur_formated_instances = []
            for j in range(len(raw_retrieved_instances['ids'][i])):
                tmp_inst = {requested_field[:-1]: raw_retrieved_instances[requested_field][i][j] 
                        for requested_field in includes + ['ids']}
                cur_distance = raw_retrieved_instances['distances'][i][j]

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
    model_name_or_path: str = '../models/intfloat/multilingual-e5-small'
    prompts: Dict = field(default_factory=lambda: {"query": "query: ", "passage": "passage: "})
    device: str = 'cuda'
    normalize_embeddings: bool = True

class EmbedderModel:
    def __init__(self, config: EmbedderModelConfig = None) -> None:
        self.config = EmbedderModelConfig() if config is None else config
        self.model = SentenceTransformer(
            config.model_name_or_path, device=config.device,
            prompts=config.prompts
        )

    def encode_queries(self, queries: List[str], **kwargs) -> List[List[float]]:
        return self.model.encode(queries, prompt_name='query', 
                                 normalize_embeddings=self.config.normalize_embeddings, **kwargs)

    def encode_passages(self, passages: List[str], **kwargs) -> List[List[float]]:
        return self.model.encode(passages, prompt_name='query',
                                 normalize_embeddings=self.config.normalize_embeddings,
                                 **kwargs)


NODES_DB_DEFAULT_CONFIG = VectorDBConnectionConfig(path="../data/graph_structures/vectorized_nodes/v8/densedb", db_name="vectorized_nodes")
TRIPLETS_DB_DEFAULT_CONFIG = VectorDBConnectionConfig(path="../data/graph_structures/vectorized_triplets/v4/densedb", db_name="vectorized_triplets")

@dataclass
class EmbeddingsDatabaseConnectionConfig:
    nodes_db_config: VectorDBConnectionConfig = field(default_factory=lambda: NODES_DB_DEFAULT_CONFIG) 
    triplets_db_config: VectorDBConnectionConfig = field(default_factory=lambda: TRIPLETS_DB_DEFAULT_CONFIG)
    embedder_config: EmbedderModelConfig = field(default_factory=lambda: EmbedderModelConfig())

#
AVAILABLE_VECTODB_CONNECTORS = {
    'chroma': ChromaConnection
}

class EmbeddingsDatabaseConnection:
    def __init__(self, config: EmbeddingsDatabaseConnectionConfig = EmbeddingsDatabaseConnectionConfig()):
        self.vectordbs = {
            'nodes': AVAILABLE_VECTODB_CONNECTORS[config.nodes_db_config.db_vendor](config.nodes_db_config),
            'triplets': AVAILABLE_VECTODB_CONNECTORS[config.triplets_db_config.db_vendor](config.triplets_db_config)}
        self.embedder = EmbedderModel(config.embedder_config)

    def add_triplets(self, triplets:List[Triplet], add_nodes:bool=True, batch_size:int=64)->None:
        unique_nodes_ids = [] if add_nodes else None

        batch_count = math.ceil(len(triplets) / batch_size)
        for batch_idx in range(batch_count):
            triplets_ids, triplets_str = [], []
            nodes_ids, nodes_str = ([], []) if add_nodes else (None, None)

            for triplet_idx in range(batch_idx*batch_size, (batch_idx+1)*batch_size):
                triplet = triplets[triplet_idx]
                _, triplet_str =  TripletCreator.stringify(triplet) if triplet.stringified is None else (triplet.id, triplet.stringified) 
                triplets_ids.append(triplet.id)
                triplets_str.append(triplet_str)
                
                if add_nodes:
                    for node in [triplet.start_node, triplet.end_node]:
                        if node.id not in unique_nodes_ids:
                            _, node_str = NodeCreator.stringify(node) if node.stringified is None else (node.id, node.stringified)
                            unique_nodes_ids.append(node.id)
                            nodes_ids.append(node.id)                        
                            nodes_str.append(node_str)

            self.add_stringified_triplets(triplets_ids, triplets_str, nodes_ids, nodes_ids)

    def delete_triplets(self, triplets: List[Triplet], delete_nods: bool = True):
        triplets_ids = list(map(lambda v: v.id, triplets))
        
        unique_nodes_ids = None
        if delete_nods:
            nodes_ids = []
            nodes_ids += [triplet.start_node.id for triplet in triplets]
            nodes_ids += [triplet.end_node.id for triplet in triplets]
            unique_nodes_ids = list(set(nodes_ids))

        self.delete_stringified_triplets(triplets_ids, unique_nodes_ids)

    def add_stringified_triplets(self, triplets_ids: List[str], stringified_triplets: List[str], 
                     nodes_ids: List[str] = None, stringified_nodes: List[str] = None) -> None:
        self.add_instances('triplets', triplets_ids, stringified_triplets)
        if nodes_ids is not None:
            self.add_instances('nodes', nodes_ids, stringified_nodes)

    def delete_stringified_triplets(self, triplets_ids: List[str], nodes_ids: List[str] = None) -> None:
        self.delete_instances('triplets', triplets_ids)
        if nodes_ids is not None:
            self.delete_instances('nodes', nodes_ids)
    
    def add_instances(self, db_type: str, ids: List[str], stringified_instances: List[str]) -> None:
        embs = self.embedder.encode_passages(stringified_instances)
        formated_instances = [VectorDBInstance(id=id, document=doc, embedding=emb) 
                            for id, doc, emb in zip(ids, stringified_instances, embs)]
        self.vectordbs[db_type].create(formated_instances)

    def delete_instances(self, db_type: str, ids: List[str]) -> None:
        self.vectordbs[db_type].delete(ids)

    def get_embbeddings(self, db_type: str, ids: List[str]) -> List[List[float]]:
        instances = self.vectordbs[db_type].read(ids, includes=['embeddings'])
        embeddings = list(map(lambda inst: inst.embedding, instances))
        return embeddings