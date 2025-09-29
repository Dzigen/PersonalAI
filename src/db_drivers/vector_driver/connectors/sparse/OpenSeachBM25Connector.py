from typing import List, Tuple
import sys
import gc
import numpy as np

from .configs import DEFAULT_OPENSEARCH_BM25_CONFIG
from ...utils import VectorDBConnectionConfig, AbstractVectorDatabaseConnection, VectorDBInstance
from .....utils.errors import ReturnInfo


class OpenSeachBM25Connector(AbstractVectorDatabaseConnection):

    def __init__(self, config: VectorDBConnectionConfig = DEFAULT_OPENSEARCH_BM25_CONFIG) -> None:
        self.config = config
        # TODO

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
            self, query_instances: List[VectorDBInstance], n_results: int = 50, subset_ids=None,
            includes: List[str] = ['embeddings', 'documents', 'metadatas']) -> List[List[Tuple[float, VectorDBInstance]]]:
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
