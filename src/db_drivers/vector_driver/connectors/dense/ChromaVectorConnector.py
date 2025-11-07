from typing import List, Tuple, Union, Dict
import sys
import chromadb
from chromadb.config import Settings
import logging
import gc
import torch
import numpy as np
from copy import deepcopy

from .configs import DEFAULT_CHROMA_CONFIG
from ...embedders import EmbedderModel
from ...utils import VectorDBConnectionConfig, AbstractVectorDatabaseConnection, VectorDBInstance
from .....utils.errors import ReturnInfo

__import__('pysqlite3')
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
logging.getLogger("chromadb").setLevel(logging.CRITICAL)


settings = Settings(
    chroma_segment_cache_policy="LRU",
    chroma_memory_limit_bytes=50000000000  # ~50GB
)


class ChromaVectorConnection(AbstractVectorDatabaseConnection):

    def __init__(self, config: Union[Dict, VectorDBConnectionConfig] = DEFAULT_CHROMA_CONFIG,
                 embedder: Union[None, EmbedderModel] = None, encode_batchsize: int = 16) -> None:
        if isinstance(config, dict):
            config: VectorDBConnectionConfig = VectorDBConnectionConfig.from_dict(config)
        else:
            config.formate_fields()
        self.config = config

        self.embedder = embedder
        self.encode_batchsize = encode_batchsize
        self.collection = None
        self.client = None

        # self.settings = Settings(
        #     chroma_segment_cache_policy="LRU",
        #     chroma_memory_limit_bytes=50000000000  # ~50GB
        # )

    def open_connection(self) -> ReturnInfo:
        self.client = chromadb.PersistentClient(path=f"{self.config.conn['path']}/{self.config.db_info['db']}")
        self.collection = self.client.get_or_create_collection(
            name=self.config.db_info['table'], metadata=self.config.params)

        if self.config.need_to_clear:
            self.clear()

    def is_open(self) -> bool:
        # TODO
        pass

    def close_connection(self) -> ReturnInfo:
        self.collection = None
        self.client = None
        gc.collect()

    def create(self, items: List[VectorDBInstance]) -> ReturnInfo:
        # validating
        for item in items:
            if not isinstance(item.id, str):
                raise ValueError
            if type(item.embedding) in [torch.Tensor, np.ndarray]:
                raise ValueError
        unique_ids = set(map(lambda item: item.id, items))
        if len(items) != len(unique_ids):
            raise ValueError

        # Если в классе указан embedder, то используем его
        # для векторизации входящих документов
        if self.embedder is not None:
            for item in items:
                if item.embedding is not None:
                    raise ValueError

            item_documents = list(map(lambda itm: itm.document, items))
            document_embeddings = self.embedder.encode_passages(item_documents, batch_size=self.encode_batchsize)
            updated_items = []
            for i in range(len(items)):
                updated_item = deepcopy(items[i])
                updated_item.embedding = document_embeddings[i]
                updated_items.append(updated_item)

        else:
            updated_items = items
        #
        insts_idxs = list(range(len(updated_items)))
        insts_with_md = list(filter(lambda i: len(
            updated_items[i].metadata.keys()) > 0, insts_idxs))
        insts_wo_md = set(insts_idxs).difference(set(insts_with_md))

        if len(insts_with_md) > 0:
            self.collection.add(
                documents=list(
                    map(lambda idx: updated_items[idx].document, insts_with_md)),
                embeddings=list(
                    map(lambda idx: updated_items[idx].embedding, insts_with_md)),
                metadatas=list(
                    map(lambda idx: updated_items[idx].metadata, insts_with_md)),
                ids=list(map(lambda idx: updated_items[idx].id, insts_with_md)))

        if len(insts_wo_md) > 0:
            self.collection.add(
                documents=list(
                    map(lambda idx: updated_items[idx].document, insts_wo_md)),
                embeddings=list(
                    map(lambda idx: updated_items[idx].embedding, insts_wo_md)),
                ids=list(map(lambda idx: updated_items[idx].id, insts_wo_md)))

    def read(self, ids: List[str], includes: List[str] = ['embeddings', 'documents', 'metadatas']) -> List[VectorDBInstance]:
        formates_instances = []
        if len(ids):
            raw_instances = self.collection.get(
                include=includes,
                ids=ids)

            for i in range(len(raw_instances['ids'])):
                tmp_inst = {requested_field[:-1]: raw_instances[requested_field][i]
                            for requested_field in includes + ['ids']}
                if ('metadata' in list(tmp_inst.keys())) and (tmp_inst['metadata'] is None):
                    tmp_inst['metadata'] = dict()

                formates_instances.append(VectorDBInstance(**tmp_inst))

        return formates_instances

    def update(self) -> ReturnInfo:
        # TODO
        pass

    def upsert(self, items: List[VectorDBInstance]) -> None:
        # validation
        for item in items:
            if not isinstance(item.id, str):
                raise ValueError
        unique_ids = set(map(lambda item: item.id, items))
        if len(items) != len(unique_ids):
            raise ValueError

        for item in items:
            if self.item_exist(item.id):
                self.delete([item.id])
            self.create([item])

    def delete(self, ids: List[str]) -> None:
        # validation
        for id in ids:
            if not isinstance(id, str):
                raise ValueError

        if len(ids):
            self.collection.delete(ids=ids)

    def retrieve(
            self, query_instances: List[VectorDBInstance], n_results: int = 50, subset_ids: Union[None, List[str]] = None,
            includes: List[str] = ['documents', 'metadatas']) -> List[List[Tuple[float, VectorDBInstance]]]:
        self.validate_retrieve_arguments(query_instances, n_results, subset_ids, includes)
        if subset_ids is not None and len(subset_ids) < 1:
            return [[] * len(query_instances)]
        if n_results < 1:
            return [[] * len(query_instances)]

        query_instances = deepcopy(query_instances)

        collection_size = self.count_items()
        n_results = collection_size if collection_size < n_results else n_results
        if n_results < 1:
            return [[] * len(query_instances)]

        filtering_expr = dict()
        if subset_ids is not None:
            results = self.collection.get(ids=subset_ids, include=[])
            returned_ids = results['ids']
            if len(returned_ids) < 1:
                return [[] * len(query_instances)]
            filtering_expr['ids'] = returned_ids

        # Если в классе указан embedder, то используем его
        # для векторизации входящих запросов
        if self.embedder is not None:
            items_wo_embeddings: List[Tuple[str, str]] = list()
            for idx, item in enumerate(query_instances):
                if item.embedding is None:
                    items_wo_embeddings.append((idx, item.document))

            doc_wo_embeddings = list(map(lambda itm: itm[1], items_wo_embeddings))
            new_doc_embeddings = self.embedder.encode_queries(doc_wo_embeddings, batch_size=self.encode_batchsize)
            for doc_info, doc_emb in zip(items_wo_embeddings, new_doc_embeddings):
                query_instances[doc_info[0]].embedding = doc_emb

        # Attention: в случае использования ip-метрики будут получены значения расстояний [distances] между векторами,
        # а не значения их семантической блозости [similarity]
        raw_retrieved_instances = self.collection.query(
            query_embeddings=[inst.embedding for inst in query_instances],
            include=includes + ['distances'], n_results=n_results, **filtering_expr)

        #
        formated_instances = []
        for i in range(len(query_instances)):
            cur_formated_instances = []
            for j in range(len(raw_retrieved_instances['ids'][i])):
                tmp_inst = {requested_field[:-1]: raw_retrieved_instances[requested_field][i][j]
                            for requested_field in includes + ['ids']}
                cur_distance = float(raw_retrieved_instances['distances'][i][j])

                if ('metadata' in list(tmp_inst.keys())) and (tmp_inst['metadata'] is None):
                    tmp_inst['metadata'] = dict()

                # Attention: переводим значение расстояния [distance] между векторами к значению их семантической блозости [similarity]
                cur_formated_instances.append(
                    (1 - cur_distance, VectorDBInstance(**tmp_inst)))

            cur_formated_instances = sorted(
                cur_formated_instances, key=lambda v: v[0], reverse=True)
            formated_instances.append(cur_formated_instances)

        return formated_instances

    def count_items(self) -> int:
        return self.collection.count()

    def item_exist(self, id: str) -> bool:
        # validation
        if not isinstance(id, str):
            raise ValueError

        output = self.collection.get(ids=[id])
        return len(output['ids']) > 0

    def clear(self) -> None:
        self.client.delete_collection(name=self.config.db_info['table'])
        self.collection = self.client.create_collection(
            name=self.config.db_info['table'], metadata=self.config.params)
