from dataclasses import dataclass
from typing import List, Union, Tuple
from copy import deepcopy
from .utils import AbstractRerankerModule
from ..utils import BaseRerankerModuleConfig
from ...db_drivers.vector_driver import VectorComposer, VectorDBInstance


@dataclass
class SingleStepRerankerConfig(BaseRerankerModuleConfig):
    vdb_name: str
    threshold: Union[None, float] = 0.5
    fetch_n: int = 10

    def to_str(self) -> str:
        return f"{self.vdb_name}:{self.threshold}:{self.fetch_n}"


class SingleStepReranker(AbstractRerankerModule):
    def __init__(self, config: SingleStepRerankerConfig, vdb_composer: VectorComposer):
        self.config = config
        self.validate_config(vdb_composer)

        self.vdb_composer = vdb_composer

    def validate_config(self, vdb_composer: VectorComposer) -> bool:
        if self.config.vdb_name not in vdb_composer.vdb_conn_mapping.keys():
            raise ValueError
        if isinstance(self.config.threshold, float):
            if self.config.threshold < 0 or self.config.threshold > 1:
                raise ValueError
        elif self.config.threshold is not None:
            raise ValueError
        if self.config.fetch_n < 0:
            raise ValueError

        return True

    def validate_run_arguments(self, query: str, top_k: int = 1, subset_ids: Union[None, List[str]] = None,
                               includes: List[str] = ['documents', 'metadatas'], return_with_embeddings: bool = False,
                               return_with_scores: bool = False) -> bool:
        if not isinstance(query, str):
            raise TypeError
        if len(query) < 1:
            raise ValueError
        if not isinstance(top_k, int):
            raise TypeError
        if top_k < 0:
            raise ValueError
        if not isinstance(return_with_embeddings, bool):
            return TypeError
        if not isinstance(return_with_scores, bool):
            return TypeError
        return True

    def run(self, query: str, top_k: int = 1, subset_ids: Union[None, List[str]] = None,
            includes: List[str] = ['documents', 'metadatas'], return_with_embeddings: bool = False,
            return_with_scores: bool = False) -> Union[List[Tuple[float, VectorDBInstance]], List[VectorDBInstance]]:
        # self.validate_config(self.vdb_composer)
        self.validate_run_arguments(
            query, top_k, subset_ids, includes,
            return_with_embeddings, return_with_scores
        )

        include_fields = deepcopy(includes)
        if return_with_embeddings:
            include_fields.append('embeddings')

        q_instance = VectorDBInstance(document=query)

        raw_instances = self.vdb_composer.vdb_conn_mapping[self.config.vdb_name].retrieve(
            [q_instance], n_results=self.config.fetch_n, subset_ids=subset_ids, includes=include_fields)[0]
        print(raw_instances)

        if self.config.threshold is not None:
            filtered_instances = list(filter(lambda inst: inst[0] >= self.config.threshold, raw_instances))
        else:
            filtered_instances = raw_instances

        if return_with_scores:
            formated_instances = filtered_instances[:top_k]
        else:
            formated_instances = list(map(lambda inst: inst[1], filtered_instances[:top_k]))

        return formated_instances
