from typing import List, Tuple, Union
from time import sleep
from haystack_integrations.document_stores.weaviate import WeaviateDocumentStore
from haystack_integrations.components.retrievers.weaviate import WeaviateBM25Retriever
from haystack.document_stores.types import DuplicatePolicy
from haystack import Document

from .configs import DEFAULT_WEAVIATE_BM25_CONFIG
from ...utils import VectorDBConnectionConfig, AbstractVectorDatabaseConnection, VectorDBInstance
from .....utils.errors import ReturnInfo


class WeaviateBM25Connector(AbstractVectorDatabaseConnection):

    def __init__(self, config: VectorDBConnectionConfig = DEFAULT_WEAVIATE_BM25_CONFIG, **kwargs) -> None:
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
        # TODO
        pass

    def create(self, items: List[VectorDBInstance]) -> ReturnInfo:
        # validating
        for item in items:
            if not isinstance(item.id, str):
                raise ValueError
            if item.embedding is not None:
                raise ValueError
        unique_ids = set(map(lambda item: item.id, items))
        if len(items) != len(unique_ids):
            raise ValueError

        formated_items = list(map(lambda item: Document(id=item.id, content=item.document, meta=item.metadata), items))
        self.db_conn.write_documents(formated_items, policy=DuplicatePolicy.SKIP)

    def read(self, ids: List[str], includes: List[str] = ['documents', 'metadatas']) -> List[VectorDBInstance]:
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
        # validation
        for item in items:
            if not isinstance(item.id, str):
                raise ValueError
        unique_ids = set(map(lambda item: item.id, items))
        if len(items) != len(unique_ids):
            raise ValueError

        self.db_conn.delete_documents(document_ids=list(map(lambda item: item.id, items)))
        self.create(items)

    def delete(self, ids: List[str]) -> None:
        # validation
        for id in ids:
            if not isinstance(id, str):
                raise ValueError

        if len(ids):
            self.db_conn.delete_documents(document_ids=ids)

    def retrieve(self, query_instances: List[VectorDBInstance], n_results: int = 50, subset_ids: Union[None, List[str]] = None,
                 includes: List[str] = ['documents', 'metadatas']) -> List[List[Tuple[float, VectorDBInstance]]]:
        if len(query_instances) < 1:
            return ValueError
        for inst in query_instances:
            if inst.embedding is not None:
                raise ValueError

        if n_results < 1:
            return [[] * len(query_instances)]

        filters = None
        if subset_ids is not None:
            filters = {"field": "id", "operator": "in", "value": subset_ids}

        formated_outputs = []
        for query in query_instances:
            # Attention: Будут получены значения семантической близости [similarity], а не значения их расстояния [distance]
            raw_output = self.retriever.run(query=query.document, top_k=n_results, filters=filters, scale_score=True)

            formated_output = []
            for raw_item in raw_output["documents"]:
                formated_item = VectorDBInstance(id=raw_item.id)
                if 'documents' in includes:
                    formated_item.document = raw_item.content
                if 'metadatas' in includes:
                    formated_item.metadata = raw_item.meta
                formated_output.append((raw_item.score, formated_item))

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
        if self.db_conn.collection is not None:
            collection_name = f"{self.config.db_info['db']}_{self.config.db_info['table']}"
            self.db_conn.collection.delete(collection_name)
            sleep(1)
            self.db_conn.collection.create(collection_name)
            sleep(1)
