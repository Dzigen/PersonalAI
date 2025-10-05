from dataclasses import dataclass
from enum import Enum
from typing import List, Union, Dict
from .utils import AbstractRerankerModule
from ..utils import BaseRerankerModuleConfig
from ..filters.configs import AVAILABLE_FILTER_METHODS
from ...db_drivers.vector_driver import VectorComposer, VectorDBInstance
from ...agents.utils import AbstractAgentConnector


class RerankingType(Enum):
    filter = 'filter'  # sorting with tail-cuting; relevance-scores are not returning
    retriever = 'retriever'  # retrieve from ids-subset; relevance-scores are returning


@dataclass
class RerankStep:
    type: RerankingType
    name: str
    fetch_n: Union[None, int] = 10
    extended_params: Union[None, Dict] = None


@dataclass
class MultiStepRerankerConfig(BaseRerankerModuleConfig):
    reranking_sequence: List[RerankStep]


class MultiStepReranker(AbstractRerankerModule):
    def __init__(self, config: MultiStepRerankerConfig, vdb_composer: VectorComposer, availabel_agents: Union[None, Dict[str, AbstractAgentConnector]] = None):
        self.config = config
        self.validate_config(vdb_composer)

        self.vdb_composer = vdb_composer
        self.filters_mapping = dict()

    def validate_config(self, vdb_composer: VectorComposer) -> bool:
        if not isinstance(self.config.reranking_sequence, list):
            raise ValueError

        else:
            for r_config in self.config.reranking_sequence:
                if not isinstance(r_config.type, RerankingType):
                    raise ValueError

                if r_config.type == RerankingType.retriever:
                    if r_config.name not in vdb_composer.vdb_conn_mapping.keys():
                        raise ValueError
                    if r_config.extended_params is not None:
                        if ('threshold' in r_config.extended_params) and (isinstance(r_config.extended_params['threshold'], float)):
                            if r_config.extended_params['threshold'] < 0 or r_config.extended_params['threshold'] > 1:
                                raise ValueError
                        elif r_config.extended_params['threshold'] is not None:
                            raise ValueError

                elif r_config.type == RerankingType.filter:
                    if r_config.name not in AVAILABLE_FILTER_METHODS:
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
        # self.validate_config(self.vdb_composer)
        self.validate_run_arguments(query, top_k, return_with_embeddings)

        q_instance = VectorDBInstance(document=query)
        sorted_subset_ids = None
        for r_config in self.config.reranking_sequence:
            if r_config.type == RerankingType.retriever:
                fetch_n, threshold = r_config.fetch_n, None if r_config.extended_params is None else r_config.extended_params.get('threshold', None)
                vdb_name = r_config.name

                instances = self.vdb_composer.vdb_conn_mapping[vdb_name].retrieve([q_instance], n_results=fetch_n, subset_ids=sorted_subset_ids)[0]

                if threshold is not None:
                    filtered_instances = list(filter(lambda inst: inst[0] > threshold, instances))
                else:
                    filtered_instances = instances

                sorted_subset_ids = list(map(lambda inst: inst[1].id, filtered_instances))

            elif r_config.type == RerankingType.filter:
                # TODO
                raise NotImplementedError
            else:
                raise ValueError

        sorted_subset_ids = sorted_subset_ids[:top_k]
        includes = ['documents', 'metadatas']
        if isinstance(return_with_embeddings, str):
            vdb_name = return_with_embeddings
            includes.append('embeddings')
        else:
            vdb_name = None
        final_instances = self.vdb_composer.read(sorted_subset_ids, vdb_name=vdb_name, includes=includes)

        return final_instances
