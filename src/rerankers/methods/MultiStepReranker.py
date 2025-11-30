from dataclasses import dataclass
from enum import Enum
from typing import List, Union, Dict, Tuple
from collections import defaultdict
from copy import deepcopy

from .utils import AbstractRerankerModule
from ..utils import BaseRerankerModuleConfig
from ..filters.configs import AVAILABLE_FILTER_METHODS
from ...db_drivers.vector_driver import VectorComposer, VectorDBInstance
from ...agents.utils import AbstractAgentConnector


class RerankingType(Enum):
    filter = 'filter'  # sorting with tail-cutting; relevance-scores are not returning
    retriever = 'retriever'  # retrieve from ids-subset; relevance-scores are returning


MS_RERANKING_TYPES_MAP = {
    'filter': RerankingType.filter,
    'retriever': RerankingType.retriever
}


@dataclass
class RerankStep:
    """Конфигурация отдельной стадии в рамках многостадийного Retrieve/Rerank-оператора

    :param type: Тип стадии: (1) 'retriever' - выполняется извлечение релевантных элементов к запросу на основе семантической близости их векторных представлений, которые заранее подготовлены и доступны через соответствующий коннектор к векторной бд; (2) 'filter' - выполняется переранжирование/фильтрацию ранее извлечённых элементов без использования коннекторов к БД с заранее посчитанных векторных представлений элементов.
    :type type: Union[str,RerankingType]
    :param name: Название (ключевое слово) набора логики для выполнения на данной стадии. В случае 'retrieve'-значения в type-поле данное название должно отсылать к vectordb-коннектору из заданного Vector-компоновщика при инициализации MultiStepReranker-класса. В случае 'filter'-значения в type-поле название отсылает к одному из реализованных/поддерживаемых filter-операторов в библиотеке.
    :type name: str
    :param fetch_n: Базовое количество релевантных элементов к запросу (query), которое извлекается перед выполнением filter-операций. Значение по умолчанию 10.
    :type fetch_n: Union[None, int], optional
    :param extended_params: Дополнительные параметры стадии. Значение по умолчанию None.
    :type extended_params: Union[None, Dict], optional
    """
    type: Union[str, RerankingType]
    name: str
    fetch_n: Union[None, int] = 10
    extended_params: Union[None, Dict] = None

    def to_str(self) -> str:
        str_extended_params = [f"{k}:{v}" for k, v in self.extended_params.items()]
        return f"{self.type}:{self.name}:{self.fetch_n}:{str_extended_params}"

    def formate_fields(self):
        if isinstance(self.type, str):
            self.type = MS_RERANKING_TYPES_MAP[self.type]


@dataclass
class MultiStepRerankerConfig(BaseRerankerModuleConfig):
    """Конфигурация многостадийного Retrieve/Rerank-оператора

    :param reranking_sequence: Последовательность вызова и конфигурации стадий для извлечения и переранжирования.
    :type reranking_sequence: List[Union[Dict,RerankStep]]
    """
    reranking_sequence: List[Union[Dict, RerankStep]]

    @staticmethod
    def from_dict(dict_config: Dict):
        dictconfig_copy = deepcopy(dict_config)
        formated_config = MultiStepRerankerConfig(**dictconfig_copy)
        formated_config.formate_fields()
        return formated_config

    def formate_fields(self):
        for i, rstep_config in enumerate(self.reranking_sequence):
            if isinstance(rstep_config, dict):
                formated_rstep_config = RerankStep(**rstep_config)
                formated_rstep_config.formate_fields()
                self.reranking_sequence[i] = formated_rstep_config
            else:
                rstep_config.formate_fields()


class MultiStepReranker(AbstractRerankerModule):
    """Класс реализует логику многостадийного Retrieve/Rerank-оператора для поиска релевантных элементов в заданном наборе к запросу
    с помощью оценки семантической близости их различных вариантов векторных представлений.

    :param config: Конфигурация Retrieve/Rerank-оператора.
    :type config: Union[Dict, MultiStepRerankerConfig]
    :param vdb_composer: Компоновщик нескольких наборов векторных представлений для одной группы элементов, из которой будет выполняться извлечение (retrieve/rerank-операция).
    :type vdb_composer: VectorComposer
    :param available_agents: Доступные именованные коннекторы к LLM-агентам для использования в рамках обозначенных retrieve/filter-стадий. Значение по умолчанию None.
    :type available_agents: Union[None, Dict[str, AbstractAgentConnector]], optional
    """

    def __init__(self, config: Union[Dict, MultiStepRerankerConfig], vdb_composer: VectorComposer,
                 available_agents: Union[None, Dict[str, AbstractAgentConnector]] = None):
        if isinstance(config, dict):
            config: MultiStepRerankerConfig = MultiStepRerankerConfig.from_dict(config)
        else:
            config.formate_fields()
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
                        raise ValueError(f"{r_config.name} not in {vdb_composer.vdb_conn_mapping.keys()}")
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

    def validate_run_arguments(self, query: str, top_k: int, subset_ids: Union[None, List[str]], includes: List[str],
                               return_with_embeddings: Union[str, bool], return_with_scores: Union[str, bool]) -> bool:
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

        if isinstance(return_with_scores, str):
            vdb_name = return_with_scores
            if vdb_name not in self.vdb_composer.vdb_conn_mapping.keys():
                raise ValueError
        elif return_with_scores:
            raise ValueError

        if subset_ids is not None:
            for cur_id in subset_ids:
                assert isinstance(cur_id, str)

        if isinstance(includes, list):
            for name in includes:
                if not ((isinstance(name, str)) and (name in ['documents', 'metadatas'])):
                    raise ValueError
        else:
            raise ValueError

        return True

    def run(self, query: str, top_k: int = 1, subset_ids: Union[None, List[str]] = None,
            includes: List[str] = ['documents', 'metadatas'], return_with_embeddings: Union[str, bool] = False,
            return_with_scores: bool = False) -> Union[List[Tuple[float, VectorDBInstance]], List[VectorDBInstance]]:
        # self.validate_config(self.vdb_composer)
        self.validate_run_arguments(
            query, top_k, subset_ids, includes,
            return_with_embeddings, return_with_scores)

        q_instance = VectorDBInstance(document=query)
        sorted_subset_ids = deepcopy(subset_ids)
        id_to_score: Dict[str, Dict[str, Union[float]]] = defaultdict(
            lambda: {r_config.name: None for r_config in self.config.reranking_sequence if r_config.type == RerankingType.retriever})
        for i, r_config in enumerate(self.config.reranking_sequence):
            if r_config.type == RerankingType.retriever:
                fetch_n, threshold = r_config.fetch_n, None if r_config.extended_params is None else r_config.extended_params.get('threshold', None)
                vdb_name = r_config.name

                instances = self.vdb_composer.vdb_conn_mapping[vdb_name].retrieve(
                    [q_instance], n_results=fetch_n, subset_ids=sorted_subset_ids, includes=[])[0]
                # print(f"{i}. {instances}")

                if threshold is not None:
                    filtered_instances = list(filter(lambda inst: inst[0] >= threshold, instances))
                else:
                    filtered_instances = instances

                sorted_subset_ids = []
                for raw_inst in filtered_instances:
                    id_to_score[raw_inst[1].id][r_config.name] = raw_inst[0]
                    sorted_subset_ids.append(raw_inst[1].id)

            elif r_config.type == RerankingType.filter:
                # TODO
                raise NotImplementedError
            else:
                raise ValueError

        sorted_subset_ids = sorted_subset_ids[:top_k]

        #
        include_fields = deepcopy(includes)
        if isinstance(return_with_embeddings, str):
            vdb_name = return_with_embeddings
            include_fields.append('embeddings')
        else:
            vdb_name = None
        filled_instances = self.vdb_composer.read(sorted_subset_ids, vdb_name=vdb_name, includes=include_fields)
        id_to_finst = {inst.id: inst for inst in filled_instances}
        filled_instances = [id_to_finst[inst_id] for inst_id in sorted_subset_ids]
        # print(filled_instances)

        #
        if isinstance(return_with_scores, str):
            vdb_name = return_with_scores
            scored_instances = [(float(id_to_score[inst.id][vdb_name]), inst) for inst in filled_instances]
        else:
            scored_instances = filled_instances
        # print(scored_instances)

        return scored_instances
