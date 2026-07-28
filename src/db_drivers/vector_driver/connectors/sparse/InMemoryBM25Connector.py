from typing import List, Tuple, Union, Dict
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack.components.retrievers.in_memory import InMemoryBM25Retriever
from haystack.document_stores.types import DuplicatePolicy
from haystack import Document
import pickle
import os
import hashlib
import time
import gc

from .configs import DEFAULT_INMEMORY_BM25_CONFIG
from ...utils import VectorDBConnectionConfig, AbstractVectorDatabaseConnection, VectorDBInstance
from .....utils.errors import ReturnInfo


class InMemoryBM25Connector(AbstractVectorDatabaseConnection):

    def __init__(self, config: Union[Dict, VectorDBConnectionConfig] = DEFAULT_INMEMORY_BM25_CONFIG, **kwargs) -> None:
        if isinstance(config, dict):
            config: VectorDBConnectionConfig = VectorDBConnectionConfig.from_dict(config)
        else:
            config.formate_fields()
        self.config = config

        self.db_conn = None
        self.retriever = None

    def open_connection(self) -> ReturnInfo:
        self.db_conn = InMemoryDocumentStore()

        if self.config.params['load_from_disk']:
            if self.config.params['load_dump_name'] is None:
                load_path = f"{self.config.params['load_dump_dir']}/{self.config.db_info['db']}/{self.config.db_info['table']}.json"
            else:
                load_path = f"{self.config.params['load_dump_dir']}/{self.config.params['load_dump_name']}"

            if os.path.exists(load_path):
                self.db_conn = self.db_conn.load_from_disk(load_path)
            else:
                # print(f"warning: inmemory_sparse-dump '{load_path}' doesnt exists. creating empty store")
                os.makedirs(f"{self.config.params['save_dump_dir']}/{self.config.db_info['db']}", exist_ok=True)
        else:
            os.makedirs(f"{self.config.params['save_dump_dir']}/{self.config.db_info['db']}", exist_ok=True)

        self.retriever = InMemoryBM25Retriever(document_store=self.db_conn)

        if self.config.need_to_clear:
            self.clear()

    def is_open(self) -> bool:
        # TODO
        pass

    def close_connection(self) -> ReturnInfo:
        # print("closing inmemory bm25 connection...")
        if self.db_conn is None:
            return
        elif self.config.params['save_on_disk']:
            save_path = f"{self.config.params['save_dump_dir']}/{self.config.db_info['db']}/{self.config.db_info['table']}"
            if os.path.exists(save_path) and not self.config.params['rewrite']:
                # print("warning: file on that path is already exists")
                postfix = hashlib.md5(str(time.time()).encode()).hexdigest()
                save_path += f'({postfix})'
            save_path += '.json'

            self.db_conn.save_to_disk(save_path)
            # print(f"inmemory bm25-store saved in: {save_path}")

        self.retriever = None
        self.db_conn = None
        gc.collect()

    def create(self, items: List[VectorDBInstance]) -> ReturnInfo:
        # validating
        for item in items:
            if not isinstance(item.id, str):
                raise ValueError(f"item: {item}")
            if item.embedding is not None:
                raise ValueError(f"item: {item}")
        unique_ids = set(map(lambda item: item.id, items))
        if len(items) != len(unique_ids):
            raise ValueError(f"* len(unique_ids): {len(unique_ids)}\n* len(items): {len(items)}")

        formated_items = list(map(lambda item: Document(id=item.id, content=item.document, meta=item.metadata), items))
        self.db_conn.write_documents(formated_items, policy=DuplicatePolicy.SKIP)

    def read(self, ids: List[str], includes: List[str] = ['documents', 'metadatas']) -> List[VectorDBInstance]:
        # validation
        for id in ids:
            if (id is None) or (not isinstance(id, str)):
                raise ValueError(f"* bad id: {id}\n* ids: {ids}")
        if len(ids) < 1:
            return []

        raw_output = self.db_conn.filter_documents(
            filters={"field": "id", "operator": "in", "value": ids})

        formated_output = []
        for raw_item in raw_output:
            formated_item = VectorDBInstance(id=raw_item.id)
            if 'documents' in includes:
                formated_item.document = raw_item.content
            if 'metadatas' in includes:
                formated_item.metadata = raw_item.meta
            formated_output.append(formated_item)

        return formated_output

    def update(self) -> ReturnInfo:
        # TODO
        pass

    def upsert(self, items: List[VectorDBInstance]) -> None:
        # validating
        for item in items:
            if not isinstance(item.id, str):
                raise ValueError(f"item: {item}")
            if item.embedding is not None:
                raise ValueError(f"item: {item}")
            for k, v in item.metadata.items():
                if v is None:
                    raise ValueError(f"Значение поля не должно быть None: id={item.id} | {k} = {v}")
        unique_ids = set(map(lambda item: item.id, items))
        if len(items) != len(unique_ids):
            raise ValueError(f"* len(unique_ids): {len(unique_ids)}\n* len(items): {len(items)}")

        self.db_conn.delete_documents(document_ids=list(map(lambda item: item.id, items)))
        self.create(items)

    def delete(self, ids: List[str]) -> None:
        # validation
        for id in ids:
            if not isinstance(id, str):
                raise ValueError(f"* bad id: {id}\n* ids: {ids}")

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

        filters = None
        if subset_ids is not None:
            filters = {"field": "id", "operator": "in", "value": subset_ids}

        # print(query_instances)

        formated_outputs = []
        for query in query_instances:
            # Attention: Будут получены значения семантической близости [similarity], а не значения их расстояния [distance]
            # print("query: ", query)
            raw_output = self.retriever.run(query=query.document, top_k=n_results, filters=filters, scale_score=True)
            # print("output: ", raw_output)

            formated_output = []
            for raw_item in raw_output["documents"]:
                # print(raw_item)
                formated_item = VectorDBInstance(id=raw_item.id)
                if 'documents' in includes:
                    formated_item.document = raw_item.content
                if 'metadatas' in includes:
                    formated_item.metadata = raw_item.meta
                formated_output.append((float(raw_item.score), formated_item))

            formated_outputs.append(formated_output)

        return formated_outputs

    def count_items(self) -> int:
        return self.db_conn.count_documents()

    def item_exist(self, id: str) -> bool:
        # validation
        if not isinstance(id, str):
            raise ValueError(f"id: {id}")

        res = self.db_conn.filter_documents(filters={"field": "id", "operator": "==", "value": id})

        return bool(len(res))

    def clear(self) -> None:
        del self.db_conn
        del self.retriever
        gc.collect()
        self.db_conn = InMemoryDocumentStore()
        self.retriever = InMemoryBM25Retriever(document_store=self.db_conn)

    def __del__(self):
        self.close_connection()