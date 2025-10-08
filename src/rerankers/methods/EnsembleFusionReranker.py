from dataclasses import dataclass, field
from typing import List, Union, Dict, Tuple
from enum import Enum
from itertools import chain
from collections import defaultdict
from copy import deepcopy

from .utils import AbstractRerankerModule
from ..utils import BaseRerankerModuleConfig
from ...db_drivers.vector_driver import VectorComposer, VectorDBInstance


@dataclass
class RetrieverConfig:
    """
    :param fetch_n: Служебный гиперпараметр. Значение по умолчанию 15.
    :type fetch_n: int, optional
    :param threshold: Нижний порог близости между эмбеддингами сущностей и вершин для их сопоставления (matching). Значение по умолчанию 0.5.
    :type threshold: float, optional
    """
    fetch_n: int = 15
    threshold: Union[None, float] = 0.5

    def to_str(self):
        return f"{self.fetch_n}:{self.threshold}"


@dataclass
class EnsembleFusionRerankerConfig(BaseRerankerModuleConfig):
    vdb_names: List[str]
    retriever_configs: Union[None, List[RetrieverConfig]] = None
    weights: Union[None, List[float]] = None
    c: int = 60

    def to_str(self) -> str:
        str_retriever_config = None if self.retriever_configs is None else [item.to_str() for item in self.retriever_configs]
        return f"{self.vdb_names}:{str_retriever_config}:{self.weights}:{self.c}"


class EnsembleFusionReranker(AbstractRerankerModule):
    def __init__(self, config: EnsembleFusionRerankerConfig, vdb_composer: VectorComposer):
        self.config = config
        if self.config.weights is None:
            self.config.weights = [1 / len(self.config.vdb_names)] * len(self.config.vdb_names)
        if self.config.retriever_configs is None:
            self.config.retriever_configs = [RetrieverConfig()] * len(self.config.vdb_names)

        self.validate_config(vdb_composer)

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

    def validate_run_arguments(self, query: str, top_k: int, subset_ids: Union[None, List[str]],
                               return_with_embeddings: Union[str, bool], return_with_scores: Union[bool, str]) -> bool:
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

    def run(self, query: str, top_k: int = 1, subset_ids: Union[None, List[str]] = None,
            includes: List[str] = ['documents', 'metadatas'], return_with_embeddings: Union[str, bool] = False,
            return_with_scores: Union[str, bool] = False) -> Union[List[Tuple[float, VectorDBInstance]], List[VectorDBInstance]]:
        # self.validate_config()
        self.validate_run_arguments(query, top_k, subset_ids, includes, return_with_embeddings, return_with_scores)

        q_instance = VectorDBInstance(document=query)
        doc_lists = []
        for i, vdb_name in enumerate(self.config.vdb_names):
            fetch_n, threshold = self.config.retriever_configs[i].fetch_n, self.config.retriever_configs[i].threshold

            instances = self.vdb_composer.vdb_conn_mapping[vdb_name].retrieve([q_instance], n_results=fetch_n, subset_ids=subset_ids)[0]

            if threshold is not None:
                filtered_instances = list(filter(lambda inst: inst[0] >= threshold, instances))
            else:
                filtered_instances = instances

            formated_instances = list(map(lambda inst: inst[1], filtered_instances))
            doc_lists.append(formated_instances)

        fused_instances = self.weighted_reciprocal_rank(doc_lists)[:top_k]

        include_fields = deepcopy(includes)
        if isinstance(return_with_embeddings, str):
            vdb_name = return_with_embeddings
            include_fields.append('embeddings')
            inst_ids = list(map(lambda inst: inst.id, fused_instances))
            fused_instances = self.vdb_composer.read(inst_ids, vdb_name=vdb_name, includes=include_fields)

        if isinstance(return_with_scores, str):
            vdb_name = return_with_scores
            inst_ids = list(map(lambda inst: inst.id, fused_instances))
            instances_w_scores = self.vdb_composer.vdb_conn_mapping[vdb_name].retrieve(
                [q_instance], n_results=len(inst_ids), subset_ids=inst_ids, includes=[])[0]
            id_to_score_map = {inst[1].id: inst[0] for inst in instances_w_scores}

            fused_instances = [(id_to_score_map[instance.id], instance) for instance in fused_instances]

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
