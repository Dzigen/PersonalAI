from typing import List, Tuple, Union, Dict
import faiss
from langchain_community.vectorstores import FAISS
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_core.documents import Document
from langchain_community.vectorstores.utils import DistanceStrategy
import gc
import os
import torch
from time import time
import hashlib
import numpy as np
from copy import deepcopy

from .configs import DEFAULT_INMEMORY_CONFIG
from ...embedders import EmbedderModel
from ...utils import VectorDBConnectionConfig, AbstractVectorDatabaseConnection, VectorDBInstance
from .....utils.errors import ReturnInfo


class InMemoryVectorConnector(AbstractVectorDatabaseConnection):
    # https://python.langchain.com/api_reference/community/vectorstores/langchain_community.vectorstores.faiss.FAISS.html#langchain_community.vectorstores.faiss.FAISS.delete

    def __init__(self, config: Union[Dict, VectorDBConnectionConfig] = DEFAULT_INMEMORY_CONFIG,
                 embedder: Union[None, EmbedderModel] = None, encode_batchsize: int = 16) -> None:
        if isinstance(config, dict):
            config: VectorDBConnectionConfig = VectorDBConnectionConfig.from_dict(config)
        else:
            config.formate_fields()
        self.config = config

        self.embedder = embedder
        self.encode_batchsize = encode_batchsize

        self.structure: FAISS = None

    def open_connection(self) -> ReturnInfo:
        if self.config.params['load_from_disk']:
            if self.config.params['load_dump_name'] is None:
                load_path = f"{self.config.params['load_dump_dir']}/{self.config.db_info['db']}"
                load_fname = self.config.db_info['table']
            else:
                load_path = self.config.params['load_dump_dir']
                load_fname = self.config.params['load_dump_name']

            if os.path.exists(f"{load_path}/{load_fname}"):
                self.structure = FAISS.load_local(
                    folder_path=load_path,
                    index_name=load_fname,
                    embeddings=self.embedder,)
            else:
                # print(f"warning: graph-dump '{load_path}' doesnt exists. creating empty graph-store")
                os.makedirs(f"{self.config.params['save_dump_dir']}/{self.config.db_info['db']}", exist_ok=True)
                self.structure = FAISS(
                    embedding_function=self.embedder,
                    index=faiss.IndexFlatIP(self.config.params['vector_dim']),
                    docstore=InMemoryDocstore(),
                    index_to_docstore_id={},
                    distance_strategy=DistanceStrategy.DOT_PRODUCT
                )
        else:
            os.makedirs(f"{self.config.params['save_dump_dir']}/{self.config.db_info['db']}", exist_ok=True)
            self.structure = FAISS(
                embedding_function=self.embedder,
                index=faiss.IndexFlatIP(self.config.params['vector_dim']),
                docstore=InMemoryDocstore(),
                index_to_docstore_id={},
                distance_strategy=DistanceStrategy.DOT_PRODUCT
            )

        if self.config.need_to_clear:
            self.clear()

    def is_open(self) -> bool:
        # TODO
        pass

    def close_connection(self) -> ReturnInfo:
        # print("closing inmemory graph connection...")
        if self.structure is None:
            return
        if self.config.params['save_on_disk']:
            save_path = f"{self.config.params['save_dump_dir']}/{self.config.db_info['db']}"
            save_fname = self.config.db_info['table']
            if os.path.exists(f"{save_path}/{save_fname}") and not self.config.params['rewrite']:
                # print("warning: file on that path is already exists")
                postfix = hashlib.md5(str(time.time()).encode()).hexdigest()
                save_fname += postfix

            self.structure.save_local(save_path, save_fname)

            # print(f"inmemory graph-store saved in: {save_path}")

        self.structure = None
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
            for item in items:
                if item.embedding is None:
                    raise ValueError
            updated_items = deepcopy(items)

        filtered_items: List[VectorDBInstance] = []
        for item in updated_items:
            item_exists = self.item_exist(item.id)
            if not item_exists:
                item.metadata['id'] = item.id
                filtered_items.append(item)

        print(filtered_items)

        if len(filtered_items) > 0:
            self.structure.add_embeddings(
                ids=[item.id for item in filtered_items],
                text_embeddings=[(item.document, item.embedding) for item in filtered_items],
                metadatas=[item.metadata for item in filtered_items],
            )

    def read(self, ids: List[str], includes: List[str] = ['embeddings', 'documents', 'metadatas']) -> List[VectorDBInstance]:
        # validation
        for id in ids:
            if (id is None) or (not isinstance(id, str)):
                raise ValueError
        if len(ids) < 1:
            return []

        raw_items: List[Document] = self.structure.get_by_ids(ids)
        formated_items: List[VectorDBInstance] = []
        for raw_inst in raw_items:
            cur_fitem = VectorDBInstance(
                id=raw_inst.id,
                document=raw_inst.page_content if 'documents' in includes else None,
                metadata=deepcopy(raw_inst.metadata) if 'metadatas' in includes else None
            )
            if 'metadatas' in includes:
                del cur_fitem.metadata['id']
            formated_items.append(cur_fitem)

        if 'embeddings' in includes:
            docstore_to_index_ids = {docstore_id: index_id for index_id, docstore_id in self.structure.index_to_docstore_id.items()}
            for item in formated_items:
                item.embedding = self.structure.index.reconstruct(docstore_to_index_ids[item.id]).astype(float)

        return formated_items

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

        existed_ids = list(set(ids).intersection(self.structure.index_to_docstore_id.values()))
        if len(existed_ids) > 0:
            self.structure.delete(existed_ids)

    def retrieve(
            self, query_instances: List[VectorDBInstance], n_results: int = 50, subset_ids: Union[None, List[str]] = None,
            includes: List[str] = ['documents', 'metadatas']) -> List[List[Tuple[float, VectorDBInstance]]]:
        self.validate_retrieve_arguments(query_instances, n_results, subset_ids, includes)
        if subset_ids is not None and len(subset_ids) < 1:
            return [[] * len(query_instances)]
        if n_results < 1:
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

        filter_subset = None
        if subset_ids is not None:
            filter_subset = {"id": {"$in": subset_ids}}

        formated_items = []
        for query in query_instances:
            cur_fitmes: List[Tuple[float, VectorDBInstance]] = []
            cur_output = self.structure.similarity_search_with_score_by_vector(
                embedding=query.embedding, k=n_results, filter=filter_subset)

            for doc, score in cur_output:
                cur_fitem = VectorDBInstance(
                    id=doc.id,
                    document=doc.page_content if 'documents' in includes else None,
                    metadata=deepcopy(doc.metadata) if 'metadatas' in includes else None
                )
                if 'metadatas' in includes:
                    del cur_fitem.metadata['id']
                cur_fitmes.append((float(score), cur_fitem))

            if 'embeddings' in includes:
                docstore_to_index_ids = {docstore_id: index_id for index_id, docstore_id in self.structure.index_to_docstore_id.items()}
                for item in cur_fitmes:
                    item.embedding = self.structure.index.reconstruct(docstore_to_index_ids[item.id]).astype(float)

            formated_items.append(cur_fitmes)

        return formated_items

    def count_items(self) -> int:
        return len(self.structure.index_to_docstore_id)

    def item_exist(self, id: str) -> bool:
        # validation
        if not isinstance(id, str):
            raise ValueError

        return len(self.structure.get_by_ids([id])) > 0

    def clear(self) -> None:
        del self.structure
        gc.collect()
        self.structure = FAISS(
            index=faiss.IndexFlatIP(self.config.params['vector_dim']),
            docstore=InMemoryDocstore(), index_to_docstore_id={},
            distance_strategy=DistanceStrategy.DOT_PRODUCT,
            embedding_function=self.embedder
        )
