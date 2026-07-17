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
    :param threshold: Пороговое/минимальное значение similarity-метрики, по которому выполняется дополнительная фильтрация извлечённых элементов. Если задано None-значение, то фильтрация пропускается. Значение по умолчанию 0.5.
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
    :type retriever_configs: Union[None, List[Union[Dict,RetrieverConfig]]]
    :param weights: Значения приоритета similarity-оценок соответствующих retrieve-компонент в ансамбле для переранжирования извлечённых элементов в рамках RRF-алгоритма. В сумме значения должны давать 1.0. Если будет задан None, то значение приоритета будет равномерно распределено между заданными retrieve-компонентами в ансамбле.
    :type weights: Union[None, List[float]]
    :param c: Служебный гиперпараметр для weighted RRF-алгоритма.
    :type c: int
    """
    vdb_names: List[str]
    retriever_configs: Union[None, List[Union[Dict, RetrieverConfig]]] = None
    weights: Union[None, List[float]] = None
    c: int = 60

    def to_str(self) -> str:
        str_retriever_config = None if self.retriever_configs is None else [item.to_str() for item in self.retriever_configs]
        return f"{self.vdb_names}:{str_retriever_config}:{self.weights}:{self.c}"

    @staticmethod
    def from_dict(dict_config: Dict):
        dictconfig_copy = deepcopy(dict_config)
        formated_config = EnsembleFusionRerankerConfig(**dictconfig_copy)
        formated_config.formate_fields()
        return formated_config

    def formate_fields(self):
        if isinstance(self.retriever_configs, list):
            for i, r_config in enumerate(self.retriever_configs):
                if isinstance(r_config, dict):
                    self.retriever_configs[i] = RetrieverConfig(**r_config)


class EnsembleFusionReranker(AbstractRerankerModule):
    """Класс реализует логику ансамблевого Retrieve/Rerank-оператора для поиска релевантных элементов в заданном наборе к запросу
    с помощью оценки семантической близости их различных вариантов векторных представлений и дополнительного переранжирования элементов с помощью RRF-алгоритма.

    :param config: Конфигурация Retrieve/Rerank-оператора.
    :type config: Union[EnsembleFusionRerankerConfig, Dict]
    :param vdb_composer: Компоновщик нескольких наборов векторных представлений для одной группы элементов, из которой будет выполняться извлечение (retrieve/rerank-операция).
    :type vdb_composer: VectorComposer
    """

    def __init__(self, config: Union[EnsembleFusionRerankerConfig, Dict], vdb_composer: VectorComposer):
        if isinstance(config, dict):
            config: EnsembleFusionRerankerConfig = EnsembleFusionRerankerConfig.from_dict(config)
        else:
            config.formate_fields()
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
            return_with_scores: Union[str, bool] = False) -> Union[List[Tuple[float, VectorDBInstance]], List[VectorDBInstance]]:
        # self.validate_config()
        self.validate_run_arguments(query, top_k, subset_ids, includes, return_with_embeddings, return_with_scores)

        q_instance = VectorDBInstance(document=query)
        doc_lists_ids = []
        for i, vdb_name in enumerate(self.config.vdb_names):
            fetch_n, threshold = self.config.retriever_configs[i].fetch_n, self.config.retriever_configs[i].threshold
            # print(f"{i}/{vdb_name}:")
            instances = self.vdb_composer.vdb_conn_mapping[vdb_name].retrieve(
                [q_instance], n_results=fetch_n, subset_ids=subset_ids, includes=[])[0]
            # print(instances)

            if threshold is not None:
                filtered_instances = list(filter(lambda inst: inst[0] >= threshold, instances))
            else:
                filtered_instances = instances

            doc_ids = []
            for raw_instance in filtered_instances:
                doc_ids.append(raw_instance[1].id)
            doc_lists_ids.append(doc_ids)

        fused_ids = self.weighted_reciprocal_rank(doc_lists_ids)[:top_k]
        # print(fused_ids)

        #
        include_fields = deepcopy(includes)
        vdb_name = None
        if isinstance(return_with_embeddings, str):
            vdb_name = return_with_embeddings
            include_fields.append('embeddings')
        
        # !!! PAY ATTENTION : read-method returns items in non-deterministic order !!!
        tmp_filled_instances = self.vdb_composer.read(fused_ids, vdb_name=vdb_name, includes=include_fields)
        id_to_idx = {inst_id: idx for idx, inst_id in enumerate(fused_ids)}
        filled_instances = [None] * len(fused_ids)
        for inst in tmp_filled_instances:
            filled_instances[id_to_idx[inst.id]] = inst 
        
        assert len(fused_ids) == len(filled_instances)
        # id_to_finst = {inst.id: inst for inst in filled_instances}
        # filled_instances = [id_to_finst[inst_id] for inst_id in fused_ids]
        # print(vdb_name, filled_instances)

        #
        if isinstance(return_with_scores, str):
            vdb_name = return_with_scores
            scored_instances = self.vdb_composer.vdb_conn_mapping[vdb_name].retrieve(
                [q_instance], n_results=len(fused_ids), subset_ids=fused_ids, includes=[])[0]
            # print(vdb_name, fused_ids, scored_instances)
            # print(self.vdb_composer.count_items())
            # print(len(scored_instances), len(fused_ids), set(fused_ids))
            assert len(scored_instances) == len(fused_ids)
            id_to_score = {inst[1].id: inst[0] for inst in scored_instances}
            scored_instances = [(float(id_to_score[inst.id]), inst) for inst in filled_instances]
        else:
            scored_instances = filled_instances
        # print(scored_instances)

        return scored_instances

    def weighted_reciprocal_rank(self, doc_lists_ids: List[List[str]]) -> List[str]:
        """Метод выполняет взвешенный алгоритм RRF для нескольких списков с рангами. Больше деталей о RRF содержится тут: https://plg.uwaterloo.ca/~gvcormac/cormacksigir09-rrf.pdf.

        :param doc_lists_ids: Список списков с рангами, где каждый отдельный список содержит уникальные элементы.
        :type doc_lists_ids: List[List[str]]
        :return: Финальный агрегированный список элементов, отсортированных по их взвешенному скору в порядке убывания.
        :rtype: List[str]
        """
        if len(doc_lists_ids) != len(self.config.weights):
            msg = "Number of rank lists must be equal to the number of weights."
            raise ValueError(msg)

        # Associate each doc's content with its RRF score for later sorting by it
        # Duplicated contents across retrievers are collapsed & scored cumulatively
        rrf_score: Dict[str, float] = defaultdict(float)
        for list_ids, weight in zip(doc_lists_ids, self.config.weights):
            for rank, doc_id in enumerate(list_ids, start=1):
                rrf_score[doc_id] += weight / (rank + self.config.c)

        # Docs are deduplicated by their contents
        all_doc_ids = chain.from_iterable(doc_lists_ids)
        unique_ids = []
        seen_docids = set()
        for doc_id in all_doc_ids:
            if doc_id not in seen_docids:
                unique_ids.append(doc_id)
                seen_docids.add(doc_id)

        # then sorted by their scores
        return sorted(unique_ids, reverse=True, key=lambda doc_id: rrf_score[doc_id])
