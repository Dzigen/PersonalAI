from typing import List, Tuple, Union, Dict
from time import sleep
from haystack_integrations.document_stores.weaviate import WeaviateDocumentStore
from haystack_integrations.document_stores.weaviate.document_store import generate_uuid5
from haystack_integrations.components.retrievers.weaviate import WeaviateBM25Retriever
from haystack.document_stores.types import DuplicatePolicy
from haystack import Document

from .configs import DEFAULT_WEAVIATE_BM25_CONFIG
from ...utils import VectorDBConnectionConfig, AbstractVectorDatabaseConnection, VectorDBInstance
from .....utils.errors import ReturnInfo


class WeaviateBM25Connector(AbstractVectorDatabaseConnection):

    def __init__(self, config: Union[Dict, VectorDBConnectionConfig] = DEFAULT_WEAVIATE_BM25_CONFIG, **kwargs) -> None:
        if isinstance(config, dict):
            config: VectorDBConnectionConfig = VectorDBConnectionConfig.from_dict(config)
        else:
            config.formate_fields()
        self.config = config

        self.db_conn = None
        self.retriever = None

    def open_connection(self) -> ReturnInfo:
        url = f"http://{self.config.conn['host']}:{self.config.conn['port']}"
        collection_name = f"{self.config.db_info['db']}_{self.config.db_info['table']}"
        self.db_conn = WeaviateDocumentStore(url=url, collection_settings={'class': collection_name})
        self.retriever = WeaviateBM25Retriever(document_store=self.db_conn)

    def is_open(self) -> bool:
        # TODO
        pass

    def close_connection(self) -> ReturnInfo:
        try:
            self.db_conn._client.close()
        except TypeError:
            pass

    def create(self, items: List[VectorDBInstance]) -> ReturnInfo:
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
            filters={"field": "_original_id", "operator": "in", "value": ids})

        formated_output = []
        for raw_item in raw_output:
            formated_item = VectorDBInstance(id=raw_item.id)
            if 'documents' in includes:
                formated_item.document = raw_item.content
            if 'metadatas' in includes:
                formated_item.metadata = {k: v for k, v in raw_item.meta.items() if v is not None}

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
            filters = {"field": "_original_id", "operator": "in", "value": subset_ids}

        formated_outputs = []
        for query in query_instances:
            # Attention: Будут получены значения семантической близости [similarity], а не значения их расстояния [distance]
            # print("query: ", query)
            raw_output = self.retriever.run(query=query.document, top_k=n_results, filters=filters)
            # print('output: ',raw_output)

            formated_output = []
            for raw_item in raw_output["documents"]:
                formated_item = VectorDBInstance(id=raw_item.id)
                if 'documents' in includes:
                    formated_item.document = raw_item.content
                if 'metadatas' in includes:
                    formated_item.metadata = raw_item.meta
                formated_output.append((float(raw_item.score), formated_item))

            if (subset_ids is not None) and (len(formated_output) < n_results):
                containing_ids = set(map(lambda item: item[1].id, formated_output))
                extended_ids = set()
                for sub_id in subset_ids:
                    if len(containing_ids) + len(extended_ids) >= n_results:
                        break
                    elif sub_id not in containing_ids:
                        extended_ids.add(sub_id)
                extended_output = self.read(list(extended_ids), includes=includes)
                formated_output += [(0.5, item) for item in extended_output]

            formated_outputs.append(formated_output)

        return formated_outputs

    def count_items(self) -> int:
        return self.db_conn.count_documents()

    def item_exist(self, id: str) -> bool:
        # validation
        if not isinstance(id, str):
            raise ValueError(f"id: {id}")

        uuid5 = generate_uuid5(id)
        item_exists = self.db_conn.collection.data.exists(uuid5)
        return item_exists

    def clear(self) -> None:
        if self.db_conn.collection is not None:
            collection_name = f"{self.config.db_info['db']}_{self.config.db_info['table']}"
            self.db_conn.client.collections.delete(collection_name)
            sleep(1)
            self.db_conn._client.collections.create_from_dict(self.db_conn._collection_settings)
            sleep(1)
