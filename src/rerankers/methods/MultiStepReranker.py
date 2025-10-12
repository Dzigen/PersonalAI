from dataclasses import dataclass
from enum import Enum
from typing import List, Union, Dict, Tuple
from copy import deepcopy

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
    """Конфигурация отдельной стадии в рамках многостадийного Retrieve/Rerank-оператора

    :param type: Тип стадии: (1) 'retriever' - выполняется извлечение релевантных элементов к запросу на основе семантической их векторных представлений, которые заранее подготовлены доступны через соответствующий коннектор к векторной бд; (2) 'filter' - выполняется переранжирование/фильтрация ранее извлечённых элементов без использования коннекторов к БД с заранее посчитанных векторныъ представлений элементов.
    :type type: RerankingType
    :param name: Название (ключевое слово) набора логики для выполнения на данной стадии. В случае 'retrieve'-значения в type-поле данное название должно отсылать к vectordb-коннектору из заданного Vector-компоновщика при инициализации MultiStepReranker-класса. В случае 'filter'-значения в type-поле название отсылает к одному из реализованных/поддерживаемых filter-операторов в библиотеке.
    :type name: str
    :param fetch_n: Базовое количество релевантных элементов к запросу (query), которое извлекается перед выполнением filter-операций. Значение по умолчанию 10.
    :type fetch_n: Union[None, int], optional
    :param extended_params: Дополнительные параметры стадии. Значение по умолчанию None.
    :type extended_params: Union[None, Dict], optional
    """
    type: RerankingType
    name: str
    fetch_n: Union[None, int] = 10
    extended_params: Union[None, Dict] = None

    def to_str(self) -> str:
        str_extended_params = [f"{k}:{v}" for k, v in self.extended_params.items()]
        return f"{self.type}:{self.name}:{self.fetch_n}:{str_extended_params}"


@dataclass
class MultiStepRerankerConfig(BaseRerankerModuleConfig):
    """Конфигурация многостадийного Retrieve/Rerank-оператора

    :param reranking_sequence: Последовательность вызова и конфигурации стадий для извлечения и переранжирования.
    :type reranking_sequence: List[RerankStep]
    """
    reranking_sequence: List[RerankStep]


class MultiStepReranker(AbstractRerankerModule):
    """Класс реализует логику многостадийного Retrieve/Rerank-оператора для поиска релевантных элементов в заданном наборе к запросу
    с помощью оценки семантической близости их раличных вариантов векторных представлений.

    :param config: Конфигурация Retrieve/Rerank-оператора.
    :type config: EnsembleFusionRerankerConfig
    :param vdb_composer: Компоновщий нескольких наборов векторных представлений для одной группы элементов, из которой будет выполняться извлечение (retrieve/rerank-операция).
    :type vdb_composer: VectorComposer
    :param availabel_agents: Достпные именованные коннекторы к LLM-агентам для использования в рамках обозначенных retrieve/filter-стадий. Значение по умолчанию None.
    :type availabel_agents: Union[None, Dict[str, AbstractAgentConnector]], optional
    """

    def __init__(self, config: MultiStepRerankerConfig, vdb_composer: VectorComposer,
                 availabel_agents: Union[None, Dict[str, AbstractAgentConnector]] = None):
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

        return True

    def run(self, query: str, top_k: int = 1, subset_ids: Union[None, List[str]] = None,
            includes: List[str] = ['documents', 'metadatas'], return_with_embeddings: Union[str, bool] = False,
            return_with_scores: bool = False) -> Union[List[Tuple[float, VectorDBInstance]], List[VectorDBInstance]]:
        # self.validate_config(self.vdb_composer)
        self.validate_run_arguments(
            query, top_k, subset_ids, includes,
            return_with_embeddings, return_with_scores)

        q_instance = VectorDBInstance(document=query)
        for r_config in self.config.reranking_sequence:
            if r_config.type == RerankingType.retriever:
                fetch_n, threshold = r_config.fetch_n, None if r_config.extended_params is None else r_config.extended_params.get('threshold', None)
                vdb_name = r_config.name

                instances = self.vdb_composer.vdb_conn_mapping[vdb_name].retrieve([q_instance], n_results=fetch_n, subset_ids=subset_ids, includes=[])[0]

                if threshold is not None:
                    filtered_instances = list(filter(lambda inst: inst[0] >= threshold, instances))
                else:
                    filtered_instances = instances

                subset_ids = list(map(lambda inst: inst[1].id, filtered_instances))

            elif r_config.type == RerankingType.filter:
                # TODO
                raise NotImplementedError
            else:
                raise ValueError

        include_fields = deepcopy(includes)
        if isinstance(return_with_embeddings, str):
            vdb_name = return_with_embeddings
            include_fields.append('embeddings')
        else:
            vdb_name = None
        final_instances = self.vdb_composer.read(subset_ids, vdb_name=vdb_name, includes=include_fields)

        if isinstance(return_with_scores, str):
            vdb_name = return_with_scores
            instances_w_scores = self.vdb_composer.vdb_conn_mapping[vdb_name].retrieve(
                [q_instance], n_results=len(subset_ids), subset_ids=subset_ids, includes=[])[0]
            id_to_score_map = {inst[1].id: inst[0] for inst in instances_w_scores}

            final_instances = [(id_to_score_map[instance.id], instance) for instance in final_instances]

        return final_instances
