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
    :param fetch_n: Базовое количество релевантных элементов к запросу (query), которое извлекается перед выполнением filter-операций. Значение по умолчанию 15.
    :type fetch_n: int, optional
    :param threshold: Пороговое/минимальное значение similarity-метрики, по которому выполняется дополнительная фильтрация извлечённых элементов. Если задано None-значение, то фильтрация пропускается. Значение по умолчаниб 0.5.
    :type threshold: Union[None, float], optional
    """
    fetch_n: int = 15
    threshold: Union[None, float] = 0.5

    def to_str(self):
        return f"{self.fetch_n}:{self.threshold}"


@dataclass
class EnsembleFusionRerankerConfig(BaseRerankerModuleConfig):
    """Конфигурация ансамблевого Retrieve/Rerank-оператора.

    :param vdb_names: Набор названий (ключевых слов) коннекторов к различным векторным представлениям заданного набора элементов из Vector-компоновщика, которые будут использоваться в ансамбле для получения базовых групп элементов (retrieve) и их similarity-оценок.
    :type vdb_names: List[str]
    :param retriever_configs: Конфигурации для соотвествующих retrieve-компонент в ансамбле.
    :type retriever_configs: Union[None, List[RetrieverConfig]]
    :param weights: Значения приоритета similarity-оценок соотвествующих retrieve-компонент в ансамбле для переранжирования извлечённых элементов в рамках RRF-алгоритма. В сумме значения должны давать 1.0. Если будет задан None, то значение приоритета будет равномерно распределено между заданными retrieve-компонентами в ансамбле.
    :type weights: Union[None, List[float]]
    :param c: Служебный гиперпараметр для weighted RRF-алгоритма.
    :type c: int
    """
    vdb_names: List[str]
    retriever_configs: Union[None, List[RetrieverConfig]] = None
    weights: Union[None, List[float]] = None
    c: int = 60

    def to_str(self) -> str:
        str_retriever_config = None if self.retriever_configs is None else [item.to_str() for item in self.retriever_configs]
        return f"{self.vdb_names}:{str_retriever_config}:{self.weights}:{self.c}"


class EnsembleFusionReranker(AbstractRerankerModule):
    """Класс реализует логику ансамблевого Retrieve/Rerank-оператора для поиска релевантных элементов в заданном наборе к запросу
    с помощью оценки семантической близости их раличных вариантов векторных представлений и дополнительного переранжирования элементов с помощью RRF-алгоритма.

    :param config: Конфигурация Retrieve/Rerank-оператора.
    :type config: EnsembleFusionRerankerConfig
    :param vdb_composer: Компоновщий нескольких наборов векторных представлений для одной группы элементов, из которой будет выполняться извлечение (retrieve/rerank-операция).
    :type vdb_composer: VectorComposer
    """

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
                    raise ValueError(f"{vdb_name} not in {vdb_composer.vdb_conn_mapping.keys()}")

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

    def validate_run_arguments(self, query: str, top_k: int, subset_ids: Union[None, List[str]], includes: List[str],
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
        docid_to_scores = defaultdict(lambda: {v_name: None for v_name in self.config.vdb_names})
        for i, vdb_name in enumerate(self.config.vdb_names):
            fetch_n, threshold = self.config.retriever_configs[i].fetch_n, self.config.retriever_configs[i].threshold

            instances = self.vdb_composer.vdb_conn_mapping[vdb_name].retrieve([q_instance], n_results=fetch_n, subset_ids=subset_ids)[0]

            if threshold is not None:
                filtered_instances = list(filter(lambda inst: inst[0] >= threshold, instances))
            else:
                filtered_instances = instances

            formated_instances = []
            for raw_instance in filtered_instances:
                formated_instances.append(raw_instance[1])
                docid_to_scores[raw_instance[1].id][vdb_name] = raw_instance[0]

            doc_lists.append(formated_instances)

        fused_instances = self.weighted_reciprocal_rank(doc_lists)[:top_k]

        #
        include_fields = deepcopy(includes)
        if isinstance(return_with_embeddings, str):
            vdb_name = return_with_embeddings
            include_fields.append('embeddings')
            inst_ids = list(map(lambda inst: inst.id, fused_instances))
            fused_instances = self.vdb_composer.read(inst_ids, vdb_name=vdb_name, includes=include_fields)

        #
        if isinstance(return_with_scores, str):
            vdb_name = return_with_scores
            fused_instances = [(float(docid_to_scores[instance.id][vdb_name]), instance) for instance in fused_instances]

        elif return_with_scores:
            tmp_instances = []
            for instance in fused_instances:
                weighted_score = float(sum([docid_to_scores[instance.id][vdb_name] * self.config.weights[i] for i, vdb_name in enumerate(self.config.vdb_names)]))
                tmp_instances.append((weighted_score, instance))
            fused_instances = tmp_instances

        return fused_instances

    def weighted_reciprocal_rank(self, doc_lists: List[List[VectorDBInstance]]) -> List[VectorDBInstance]:
        """Perform weighted Reciprocal Rank Fusion on multiple rank lists. You can find more details about RRF here: https://plg.uwaterloo.ca/~gvcormac/cormacksigir09-rrf.pdf.

        :param doc_list: A list of rank lists, where each rank list contains unique items.
        :type doc_list: List[List[VectorDBInstance]]
        :return: The final aggregated list of items sorted by their weighted scores in descending order.
        :rtype: List[VectorDBInstance]
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
