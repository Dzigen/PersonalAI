from typing import Dict, List, Tuple
import chromadb
import logging

from ....utils.errors import ReturnInfo
from ..utils import VectorDBConnectionConfig, AbstractVectorDatabaseConnection, VectorDBInstance
logging.getLogger("chromadb").setLevel(logging.CRITICAL)

DEFAULT_CHROMA_CONFIG = VectorDBConnectionConfig(path='./default_vectordb', db_name='vectors')

class ChromaConnection(AbstractVectorDatabaseConnection):
    def __init__(self, config: VectorDBConnectionConfig) -> None:
        self.config = config
        self.open_connection()

    def open_connection(self) -> ReturnInfo:
        self.client = chromadb.PersistentClient(path=self.config.path)
        self.collection = self.client.get_or_create_collection(name=self.config.db_name, metadata=self.config.params)

        if self.config.need_to_clear:
            self.clear()

    def is_open(self) -> bool:
        # TODO
        pass

    def close_connection(self) -> ReturnInfo:
        del self.collection
        del self.client

    def create(self, items: List[VectorDBInstance]) -> ReturnInfo:

        insts_idxs = list(range(len(items)))
        insts_with_md = list(filter(lambda i: len(items[i].metadata), insts_idxs))
        insts_wo_md = set(insts_idxs).difference(set(insts_with_md))

        if len(insts_with_md):
            self.collection.add(
                documents=list(map(lambda idx: items[idx].document, insts_with_md)),
                embeddings=list(map(lambda idx: items[idx].embedding, insts_with_md)),
                metadatas=list(map(lambda idx: items[idx].metadata, insts_with_md)),
                ids=list(map(lambda idx: items[idx].id, insts_with_md)))

        if len(insts_wo_md):
            self.collection.add(
                documents=list(map(lambda idx: items[idx].document, insts_wo_md)),
                embeddings=list(map(lambda idx: items[idx].embedding, insts_wo_md)),
                ids=list(map(lambda idx: items[idx].id, insts_wo_md)))

    def read(self, ids: List[str], includes: List[str] = ['embeddings', 'documents'], **kwargs) -> List[VectorDBInstance]:
        formates_instances = []
        if len(ids):
            raw_instances = self.collection.get(
                include=includes,
                ids=ids, **kwargs)

            for i in range(len(raw_instances['ids'])):
                tmp_inst = {requested_field[:-1]: raw_instances[requested_field][i]
                            for requested_field in includes + ['ids']}
                formates_instances.append(VectorDBInstance(**tmp_inst))

        return formates_instances

    def update(self) -> ReturnInfo:
        # TODO
        pass

    def delete(self, ids: List[str], **kwargs) -> None:
        if len(ids):
            self.collection.delete(ids=ids, **kwargs)

    def retrieve(
            self, query_instances: List[VectorDBInstance], n_results: int = 50,
            includes: List[str]  = ['embeddings', 'documents', 'metadatas'], **kwargs) -> List[List[Tuple[float, VectorDBInstance]]]:
        collection_size = self.collection.count()
        n_results = collection_size if collection_size < n_results else n_results

        raw_retrieved_instances = self.collection.query(
            query_embeddings=[inst.embedding for inst in query_instances],
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

    def count_items(self) -> int:
        return self.collection.count()

    def item_exist(self, id: str) -> bool:
        output = self.collection.get(ids=[id])
        return len(output['ids']) > 0

    def clear(self) -> ReturnInfo:
        self.client.delete_collection(name=self.config.db_name)
        self.collection = self.client.create_collection(name=self.config.db_name,
                                                        metadata=self.config.params)
