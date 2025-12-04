from typing import List, Tuple, Union, Dict
import torch
import numpy as np
from copy import deepcopy
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, PointIdsList, Filter, HasIdCondition
from qdrant_client.http.exceptions import UnexpectedResponse
from haystack_integrations.document_stores.weaviate.document_store import generate_uuid5

from .configs import DEFAULT_QDRANT_CONFIG
from ...embedders import EmbedderModel
from ...utils import VectorDBConnectionConfig, AbstractVectorDatabaseConnection, VectorDBInstance
from .....utils.errors import ReturnInfo

QD_DISTANCE_KW_MAPPING = {
    'Dot': Distance.DOT
}


class QdrantVectorConnector(AbstractVectorDatabaseConnection):

    def __init__(self, config: Union[Dict, VectorDBConnectionConfig] = DEFAULT_QDRANT_CONFIG,
                 embedder: Union[None, EmbedderModel] = None, encode_batchsize: int = 16) -> None:
        if isinstance(config, dict):
            config: VectorDBConnectionConfig = VectorDBConnectionConfig.from_dict(config)
        else:
            config.formate_fields()
        self.config = config
        self.collection_name = f"{self.config.db_info['db']}_{self.config.db_info['table']}"

        self.embedder = embedder
        self.encode_batchsize = encode_batchsize
        self.db_conn = None

    def create_collection(self):
        vectors_config = VectorParams(
            size=self.config.params['vector_dim'],
            distance=QD_DISTANCE_KW_MAPPING[self.config.params['search_metric']]
        )

        if not self.db_conn.collection_exists(collection_name=self.collection_name):
            self.db_conn._client.create_collection(
                collection_name=self.collection_name,
                vectors_config=vectors_config
            )

    def open_connection(self) -> ReturnInfo:
        url = f"http://{self.config.conn['host']}:{self.config.conn['port']}"
        self.db_conn = QdrantClient(url=url)
        self.create_collection()

    def is_open(self) -> bool:
        # TODO
        pass

    def close_connection(self) -> ReturnInfo:
        try:
            self.db_conn.close()
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

        filtered_items: List[VectorDBInstance] = []
        for item in updated_items:
            item_exists = self.item_exist(item.id)
            if not item_exists:
                filtered_items.append(item)

        if len(filtered_items) > 0:
            formated_items = list(map(lambda item: PointStruct(
                id=generate_uuid5(item.id), payload=item.metadata | {'_document': item.document, '_original_id': item.id}, vector=item.embedding), filtered_items))
            self.db_conn.upsert(collection_name=self.collection_name, points=formated_items)

    def read(self, ids: List[str], includes: List[str] = ['embeddings', 'documents', 'metadatas']) -> List[VectorDBInstance]:
        # validation
        for id in ids:
            if (id is None) or (not isinstance(id, str)):
                raise ValueError
        if len(ids) < 1:
            return []

        formated_ids = list(map(generate_uuid5, ids))
        raw_output = self.db_conn.retrieve(
            collection_name=self.collection_name,
            ids=formated_ids,
            with_payload=True,
            with_vectors='embeddings' in includes
        )

        formated_output = []
        for raw_item in raw_output:
            formated_item = VectorDBInstance(
                id=raw_item.payload['_original_id'],
                document=raw_item.payload['_document'] if 'documents' in includes else None,
                metadata=raw_item.payload if 'metadatas' in includes else None,
                embedding=raw_item.vector if 'embeddings' in includes else None
            )
            if formated_item.metadata is not None:
                del formated_item.metadata['_document']
                del formated_item.metadata['_original_id']
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

        formated_ids = list(map(lambda item: generate_uuid5(item.id), items))
        self.db_conn.delete(
            collection_name=self.collection_name,
            points_selector=PointIdsList(points=formated_ids),
            wait=True  # Optional: Wait for the operation to complete
        )
        self.create(items)

    def delete(self, ids: List[str]) -> None:
        # validation
        for id in ids:
            if not isinstance(id, str):
                raise ValueError

        if len(ids):
            formated_ids = list(map(generate_uuid5, ids))
            self.db_conn.delete(
                collection_name=self.collection_name,
                points_selector=PointIdsList(points=formated_ids),
                wait=True  # Optional: Wait for the operation to complete
            )

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
        for q_inst in query_instances:
            if q_inst.embedding is None and self.embedder is None:
                raise ValueError
            elif q_inst.embedding is not None:
                if (not isinstance(q_inst.embedding, list)) or (not isinstance(q_inst.embedding[0], float)):
                    raise ValueError

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
            formated_subsetids = list(map(generate_uuid5, subset_ids))
            filters = Filter(
                must=[
                    HasIdCondition(has_id=formated_subsetids)
                ]
            )

        formated_outputs = []
        for query in query_instances:
            # Attention: Будут получены значения семантической близости [similarity], а не значения их расстояния [distance]
            # print("query: ", query.embedding)
            try:
                raw_output = self.db_conn.query_points(
                    collection_name=self.collection_name,
                    query=query.embedding,
                    query_filter=filters,
                    with_payload=True,
                    with_vectors='embeddings' in includes,
                    limit=n_results
                )
            except UnexpectedResponse as e:
                raise ValueError(str(e))
            #print('output: ', raw_output)

            formated_output = []
            for raw_item in raw_output.points:
                formated_item = VectorDBInstance(
                    id=raw_item.payload['_original_id'],
                    document=raw_item.payload['_document'] if 'documents' in includes else None,
                    metadata=raw_item.payload if 'metadatas' in includes else None,
                    embedding=raw_item.vector if 'embeddings' in includes else None
                )
                if formated_item.metadata is not None:
                    del formated_item.metadata['_document']
                    del formated_item.metadata['_original_id']
                formated_output.append((float(raw_item.score), formated_item))

            formated_outputs.append(formated_output)

        return formated_outputs

    def count_items(self, exact: bool = True) -> int:
        raw_response = self.db_conn.count(
            collection_name=self.collection_name,
            exact=exact)
        return raw_response.count

    def item_exist(self, id: str) -> bool:
        # validation
        if not isinstance(id, str):
            raise ValueError

        formated_id = generate_uuid5(id)
        retrieved_points = self.db_conn.retrieve(
            collection_name=self.collection_name,
            ids=[formated_id], with_payload=False, with_vectors=False)
        return len(retrieved_points) > 0

    def clear(self) -> None:
        if self.db_conn.collection_exists(collection_name=self.collection_name):
            self.db_conn.delete_collection(collection_name=self.collection_name)
            self.create_collection()
