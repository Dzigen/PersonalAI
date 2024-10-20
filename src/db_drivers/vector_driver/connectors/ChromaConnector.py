from typing import Dict, List, Tuple
import chromadb
import logging

from ..utils import VectorDBConnectionConfig, AbstractVectorDatabaseConnection, VectorDBInstance
logging.getLogger("chromadb").setLevel(logging.CRITICAL)

DEFAULT_CHROMA_CONFIG = VectorDBConnectionConfig(path='./default_vectordb', db_name='vectors')

class ChromaConnection(AbstractVectorDatabaseConnection):
    def __init__(self, config: VectorDBConnectionConfig) -> None:
        self.config = config
        self.open_connection()

    def open_connection(self):
        self.client = chromadb.PersistentClient(path=self.config.path)
        self.collection = self.client.get_or_create_collection(name=self.config.db_name, metadata=self.config.params)

        if self.config.need_to_clear:
            self.clear()

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
 
    def read(self, ids: List[str], includes: List[str] = ['embeddings', 'documents'], **kwargs) -> List[VectorDBInstance]:
        """Получение объектов из базы по их идентификаторам.

        Args:
            ids (List[str]): Идентификаторы объектов.
            includes (List[str], optional): Список полей, информацию по которым нужно получить для каждого объекта. 
                                            Defaults to ['embeddings', 'documents'].

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
            includes (List[str], optional): Список полей, информацию по которым нужно получить для каждого объекта. Defaults to ['embeddings', 'documents'].

        Returns:
            List[List[Tuple[float, VectorDBInstance]]]: Списки объектов из бд, релевантных заданным query-объектам.
        """

        collection_size = self.collection.count()
        n_results = collection_size if collection_size < n_results else n_results

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
