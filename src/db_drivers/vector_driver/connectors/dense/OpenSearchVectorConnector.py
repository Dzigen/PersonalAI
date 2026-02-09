from typing import List, Tuple, Union, Dict
import urllib3
import torch
import numpy as np
import gc
from copy import deepcopy
urllib3.disable_warnings()

from opensearchpy.exceptions import RequestError
from haystack_integrations.components.retrievers.opensearch import OpenSearchEmbeddingRetriever
from haystack_integrations.document_stores.opensearch import OpenSearchDocumentStore
from haystack.document_stores.types import DuplicatePolicy
from haystack import Document

from .configs import DEFAULT_OPENSEARCH_CONFIG
from ...embedders import EmbedderModel
from ...utils import VectorDBConnectionConfig, AbstractVectorDatabaseConnection, VectorDBInstance
from .....utils.errors import ReturnInfo


class OpenSeachVectorConnector(AbstractVectorDatabaseConnection):

    def __init__(self, config: Union[Dict, VectorDBConnectionConfig] = DEFAULT_OPENSEARCH_CONFIG,
                 embedder: Union[None, EmbedderModel] = None, encode_batchsize: int = 8) -> None:
        if isinstance(config, dict):
            config: VectorDBConnectionConfig = VectorDBConnectionConfig.from_dict(config)
        else:
            config.formate_fields()
        self.config = config

        self.embedder = embedder
        self.encode_batchsize = encode_batchsize
        self.db_conn = None
        self.retriever = None

    def open_connection(self) -> ReturnInfo:
        host = f"http://{self.config.conn['host']}:{self.config.conn['port']}"
        http_auth = (self.config.conn['user'], self.config.conn['pass'])
        index = f"{self.config.db_info['db']}_{self.config.db_info['table']}"
        method_setting = {"name": "hnsw", "space_type": self.config.params['search_metric'], "engine": "nmslib"}
        self.db_conn = OpenSearchDocumentStore(
            hosts=host, http_auth=http_auth, index=index, use_ssl=True,
            verify_certs=False,  # Disables certificate verification
            ssl_assert_hostname=False,
            ssl_show_warn=False,
            embedding_dim=self.config.params['vector_dim'],
            return_embedding=True,
            method=method_setting
        )
        self.retriever = OpenSearchEmbeddingRetriever(document_store=self.db_conn)

    def is_open(self) -> bool:
        # TODO
        pass

    def close_connection(self) -> None:
        try:
            self.db_conn._client.transport.close()
        except TypeError:
            pass

    def create(self, items: List[VectorDBInstance]) -> ReturnInfo:
        # validation
        for item in items:
            if not isinstance(item.id, str):
                raise ValueError
            if type(item.embedding) in [torch.Tensor, np.ndarray]:
                raise ValueError
            for k, v in item.metadata.items():
                if v is None:
                    raise ValueError(f"Значение поля не должно быть None: id={item.id} | {k} = {v}")
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
            for item in items:
                if item.embedding is None:
                    raise ValueError
            updated_items = items

        formated_items = list(map(lambda item: Document(
            id=item.id, content=item.document, meta=item.metadata, embedding=item.embedding), updated_items))
        self.db_conn.write_documents(formated_items, policy=DuplicatePolicy.SKIP)

    def read(self, ids: List[str], includes: List[str] = ['embeddings', 'documents', 'metadatas']) -> List[VectorDBInstance]:
        # validation
        for id in ids:
            if (id is None) or (not isinstance(id, str)):
                raise ValueError
        if len(ids) < 1:
            return []

        raw_output = self.db_conn.filter_documents(
            filters={"field": "id", "operator": "in", "value": ids})

        formated_output = []
        for raw_item in raw_output:
            formated_item = VectorDBInstance(
                id=raw_item.id,
                document=raw_item.content if 'documents' in includes else None,
                metadata=raw_item.meta if 'metadatas' in includes else None,
                embedding=raw_item.embedding if 'embeddings' in includes else None
            )
            formated_output.append(formated_item)

        return formated_output

    def update(self) -> ReturnInfo:
        # TODO
        pass

    def upsert(self, items: List[VectorDBInstance]) -> None:
        # validation
        for item in items:
            if not isinstance(item.id, str):
                raise ValueError
            if type(item.embedding) in [torch.Tensor, np.ndarray]:
                raise ValueError
            for k, v in item.metadata.items():
                if v is None:
                    raise ValueError(f"Значение поля не должно быть None: id={item.id} | {k} = {v}")
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
            self.db_conn.delete_documents(document_ids=ids)

    def retrieve(
            self, query_instances: List[VectorDBInstance], n_results: int = 50, subset_ids: Union[None, List[str]] = None,
            includes: List[str] = ['documents', 'metadatas']) -> List[List[Tuple[float, VectorDBInstance]]]:
        self.validate_retrieve_arguments(query_instances, n_results, subset_ids, includes)
        if subset_ids is not None and len(subset_ids) < 1:
            return [[] * len(query_instances)]
        if n_results < 1:
            return [[] * len(query_instances)]
        if self.count_items() < 1:
            return [[] * len(query_instances)]

        query_instances: List[VectorDBInstance] = deepcopy(query_instances)

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

        filters = None
        if subset_ids is not None:
            # print(subset_ids)
            filters = {"field": "id", "operator": "in", "value": subset_ids}

            # костыль : Если количество элементов в subset_ids равно n_results,
            # то при вызове run-метода у retriever-класса будет возвращено "n_results-1"-элементов
            if n_results == len(subset_ids):
                n_results += 1

        formated_outputs = []
        for query in query_instances:
            # Attention: Будут получены значения семантической близости [similarity], а не значения их расстояния [distance]
            # print("query: ", query.embedding)
            try:
                # print(n_results, filters)
                raw_output = self.retriever.run(query_embedding=query.embedding, top_k=n_results, filters=filters)
            except RequestError as e:
                raise ValueError(str(e))
            # print('output: ',raw_output)

            formated_output = []
            for raw_item in raw_output["documents"]:
                formated_item = VectorDBInstance(
                    id=raw_item.id,
                    document=raw_item.content if 'documents' in includes else None,
                    metadata=raw_item.meta if 'metadatas' in includes else None,
                    embedding=raw_item.embedding if 'embeddings' in includes else None
                )
                formated_output.append((float(raw_item.score), formated_item))

            formated_outputs.append(formated_output)

        return formated_outputs

    def count_items(self) -> int:
        return self.db_conn.count_documents()

    def item_exist(self, id: str) -> bool:
        # validation
        if not isinstance(id, str):
            raise ValueError

        res = self.db_conn.filter_documents(filters={"field": "id", "operator": "==", "value": id})

        return bool(len(res))

    def clear(self) -> None:
        if self.db_conn._client is None:
            self.count_items()

        self.db_conn._client.indices.delete(index=self.db_conn._index)
        # assert not self.db_conn._client.indices.exists(index=self.db_conn._index)

        # self.close_connection()
        # self.open_connection()
        # gc.collect()

        self.db_conn.create_index(index=self.db_conn._index, mappings=self.db_conn._get_default_mappings())
        self.db_conn._client.indices.forcemerge(index=self.db_conn._index, only_expunge_deletes=True)
        # print("mapping: ", self.db_conn._get_default_mappings())

        # assert self.db_conn._client.indices.exists(index=self.db_conn._index)
        # self.db_conn._client.indices.refresh(index=self.db_conn._index)
