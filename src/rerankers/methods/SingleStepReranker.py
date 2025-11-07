from dataclasses import dataclass
from typing import List, Union, Tuple, Dict
from copy import deepcopy
from .utils import AbstractRerankerModule
from ..utils import BaseRerankerModuleConfig
from ...db_drivers.vector_driver import VectorComposer, VectorDBInstance


@dataclass
class SingleStepRerankerConfig(BaseRerankerModuleConfig):
    """Конфигурация одностадийного Retrieve/Rerank-оператора

    :param vdb_name: Название (ключевое слово) определённого коннектора к бд с векторными представлениями извлекаемых (retrieved) элементов, которое будут использоваться при оценке их релевантности к входящим запросам.
    :type vdb_name: str
    :param fetch_n: Базовое количество релевантных элементов к запросу (query), которое извлекается перед выполнением filter-операций. Значение по умолчанию 10.
    :type fetch_n: int
    :param threshold: Пороговое/минимальное значение similarity-метрики, по которому выполняется дополнительная фильтрация извлечённых элементов. Если задано None-значение, то фильтрация пропускается. Значение по умолчаниб 0.5.
    :type threshold: Union[None, float]
    """
    vdb_name: str
    fetch_n: int = 10
    threshold: Union[None, float] = 0.5

    def to_str(self) -> str:
        return f"{self.vdb_name}:{self.threshold}:{self.fetch_n}"

    @staticmethod
    def from_dict(dict_config: Dict):
        formated_config = SingleStepRerankerConfig(**dict_config)
        formated_config.formate_fields()
        return formated_config

    def from_dict(dict_config: Dict):
        pass


class SingleStepReranker(AbstractRerankerModule):
    """Класс реализует логику одностадийного Retrieve/Rerank-оператора для поиска релевантных элементов в заданной бд к запросу
    с помощью оценки семантической близости их векторных представлений.

    :param config: Конфигурация Retrieve/Rerank-оператора.
    :type config: Union[Dict, SingleStepRerankerConfig]
    :param vdb_composer: Компоновщий нескольких наборов векторных представлений для одной группы элементов, из которой будет выполняться извлечение (retrieve-операция).
    :type vdb_composer: VectorComposer
    """

    def __init__(self, config: Union[Dict, SingleStepRerankerConfig], vdb_composer: VectorComposer):
        if isinstance(config, dict):
            config: SingleStepRerankerConfig = SingleStepRerankerConfig.from_dict(config)
        else:
            config.formate_fields()
        self.config = config

        self.validate_config(vdb_composer)

        self.vdb_composer = vdb_composer

    def validate_config(self, vdb_composer: VectorComposer) -> bool:
        if self.config.vdb_name not in vdb_composer.vdb_conn_mapping.keys():
            raise ValueError(f"{self.config.vdb_name} not in {vdb_composer.vdb_conn_mapping.keys()}")
        if isinstance(self.config.threshold, float):
            if self.config.threshold < 0 or self.config.threshold > 1:
                raise ValueError
        elif self.config.threshold is not None:
            raise ValueError
        if self.config.fetch_n < 0:
            raise ValueError

        return True

    def validate_run_arguments(self, query: str, top_k: int, subset_ids: Union[None, List[str]],
                               includes: List[str], return_with_embeddings: bool,
                               return_with_scores: bool) -> bool:
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
        # print(raw_instances)

        if self.config.threshold is not None:
            filtered_instances = list(filter(lambda inst: inst[0] >= self.config.threshold, raw_instances))
        else:
            filtered_instances = raw_instances

        if return_with_scores:
            scored_instances = filtered_instances
        else:
            scored_instances = list(map(lambda inst: inst[1], filtered_instances))

        # print(scored_instances[:top_k])

        return scored_instances[:top_k]
