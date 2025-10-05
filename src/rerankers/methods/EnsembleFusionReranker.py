from dataclasses import dataclass, field
from typing import List, Union, Dict
from enum import Enum
from itertools import chain
from collections import defaultdict

from .utils import AbstractRerankerModule
from ..utils import BaseRerankerModuleConfig
from ...db_drivers.vector_driver import VectorComposer, VectorDBInstance


@dataclass
class RetrieverConfig:
    fetch_n: int = 10
    threshold: Union[None, float] = 0.5


@dataclass
class EnsembleFusionRerankerConfig(BaseRerankerModuleConfig):
    vdb_names: List[str]
    retriever_configs: List[RetrieverConfig]
    weights: Union[None, List[float]] = None
    c: int = 60


class EnsembleFusionReranker(AbstractRerankerModule):
    def __init__(self, config: EnsembleFusionRerankerConfig, vdb_composer: VectorComposer):
        self.config = config
        self.validate_config(vdb_composer)
        if self.config.weights is None:
            self.config.weights = [1 / len(self.config.vdb_names)] * len(self.config.vdb_names)

        self.vdb_composer = vdb_composer

    def validate_config(self, vdb_composer: VectorComposer) -> bool:
        if not isinstance(self.config.vdb_names, list):
            raise
        else:
            for vdb_name in self.config.vdb_names:
                if vdb_name not in vdb_composer.vdb_conn_mapping.keys():
                    raise ValueError

        if self.config.weights is not None:
            if not isinstance(self.config.weights, list):
                raise ValueError
            else:
                if abs(1 - sum(self.config.weights)) > 1e-5:
                    raise ValueError

        if not isinstance(self.config.retriever_configs, list):
            raise ValueError
        else:
            for r_config in self.config.retriever_configs:
                if isinstance(r_config.threshold, float):
                    if r_config.threshold < 0 or r_config.threshold > 1:
                        raise ValueError
                elif r_config.threshold is not None:
                    raise ValueError
                if r_config.fetch_n < 0:
                    raise ValueError

        return True

    def validate_run_arguments(self, query: str, top_k: int = 1, return_with_embeddings: bool = False) -> bool:
        if not isinstance(query, str):
            raise TypeError
        if len(query) < 1:
            raise ValueError

        if not isinstance(top_k, int):
            raise TypeError
        if top_k < 0:
            raise ValueError

        if isinstance(return_with_embeddings, str):
            vdb_name = return_with_embeddings
            if vdb_name not in self.vdb_composer.vdb_conn_mapping.keys():
                raise ValueError
        elif return_with_embeddings:
            raise ValueError

        return True

    def run(self, query: str, top_k: int = 1, return_with_embeddings: Union[str, bool] = False) -> List[VectorDBInstance]:
        # self.validate_config()
        self.validate_run_arguments(query, top_k, return_with_embeddings)

        q_instance = VectorDBInstance(document=query)
        doc_lists = []
        for i, vdb_name in enumerate(self.config.vdb_names):
            fetch_n, threshold = self.config.retriever_configs[i].fetch_n, self.config.retriever_configs[i].threshold

            instances = self.vdb_composer.vdb_conn_mapping[vdb_name].retrieve([q_instance], n_results=fetch_n)[0]

            if threshold is not None:
                filtered_instances = list(filter(lambda inst: inst[0] > threshold, instances))
            else:
                filtered_instances = instances

            formated_instances = list(map(lambda inst: inst[1], filtered_instances))
            doc_lists.append(formated_instances)

        fused_instances = self.weighted_reciprocal_rank(doc_lists)[:top_k]

        if isinstance(return_with_embeddings, str):
            vdb_name = return_with_embeddings
            inst_ids = list(map(lambda inst: inst.id, fused_instances))
            fused_instances = self.vdb_composer.vdb_conn_mapping[vdb_name].read(inst_ids)

        return fused_instances

    def weighted_reciprocal_rank(self, doc_lists: List[List[VectorDBInstance]]) -> List[VectorDBInstance]:
        """Perform weighted Reciprocal Rank Fusion on multiple rank lists.

        You can find more details about RRF here:
        https://plg.uwaterloo.ca/~gvcormac/cormacksigir09-rrf.pdf.

        Args:
            doc_lists: A list of rank lists, where each rank list contains unique items.

        Returns:
            list: The final aggregated list of items sorted by their weighted EnsembleF
                    scores in descending order.
        """
        if len(doc_lists) != len(self.config.weights):
            msg = "Number of rank lists must be equal to the number of weights."
            raise ValueError(msg)

        # Associate each doc's content with its RRF score for later sorting by it
        # Duplicated contents across retrievers are collapsed & scored cumulatively
        rrf_score: Dict[str, float] = defaultdict(float)
        for doc_list, weight in zip(doc_lists, self.config.weights):
            for rank, doc in enumerate(doc_list, start=1):
                rrf_score[doc.id] += weight / (rank + self.config.c)

        # Docs are deduplicated by their contents
        all_docs = chain.from_iterable(doc_lists)
        unique_docs = []
        seen_docids = set()
        for doc in all_docs:
            if doc.id not in seen_docids:
                unique_docs.append(doc)
                seen_docids.add(doc.id)

        # then sorted by their scores
        return sorted(unique_docs, reverse=True, key=lambda doc: rrf_score[doc.id])
