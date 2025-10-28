from typing import List, Tuple, Union, Dict
import sys
import chromadb
from chromadb.config import Settings
import logging
import gc
import torch
import numpy as np
from copy import deepcopy

from .configs import DEFAULT_OPENSEARCH_CONFIG
from ...embedders import EmbedderModel
from ...utils import VectorDBConnectionConfig, AbstractVectorDatabaseConnection, VectorDBInstance
from .....utils.errors import ReturnInfo


class OpenSearchVectorConnector(AbstractVectorDatabaseConnection):

    def __init__(self, config: VectorDBConnectionConfig = DEFAULT_OPENSEARCH_CONFIG,
                 embedder: Union[None, EmbedderModel] = None, encode_batchsize: int = 16) -> None:
        self.config = config
        self.embedder = embedder
        self.encode_batchsize = encode_batchsize

    def open_connection(self) -> ReturnInfo:
        # TODO
        pass

    def is_open(self) -> bool:
        # TODO
        pass

    def close_connection(self) -> ReturnInfo:
        # TODO
        pass

    def create(self, items: List[VectorDBInstance]) -> ReturnInfo:
        # TODO
        pass

    def read(self, ids: List[str], includes: List[str] = ['embeddings', 'documents', 'metadatas']) -> List[VectorDBInstance]:
        # TODO
        pass

    def update(self) -> ReturnInfo:
        # TODO
        pass

    def upsert(self, items: List[VectorDBInstance]) -> None:
        # TODO
        pass

    def delete(self, ids: List[str]) -> None:
        # TODO
        pass

    def retrieve(
            self, query_instances: List[VectorDBInstance], n_results: int = 50, subset_ids: Union[None, List[str]] = None,
            includes: List[str] = ['documents', 'metadatas']) -> List[List[Tuple[float, VectorDBInstance]]]:
        # TODO
        pass

    def count_items(self) -> int:
        # TODO
        pass

    def item_exist(self, id: str) -> bool:
        # TODO
        pass

    def clear(self) -> None:
        # TODO
        pass
