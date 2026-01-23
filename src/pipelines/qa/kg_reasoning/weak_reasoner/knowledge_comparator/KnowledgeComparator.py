from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Union
from copy import deepcopy

from .configs import KC_MAIN_LOG_PATH, KC_RERANKDRIVER_DEFAULT_CONFIG
from ......utils import Logger, ReturnStatus, ReturnInfo, accumulate_step_info
from ......utils.errors import STATUS_MESSAGE
from ......utils.data_structs import QueryInfo, create_id, NodeType, BaseComponentConfig, NodeInfo
from ......kg_model import KnowledgeGraphModel
from ......db_drivers.vector_driver import VectorDBInstance
from ......utils.cache_kv import CacheUtils
from ......db_drivers.kv_driver import KeyValueDriverConfig
from ......rerankers import RerankerDriver, RerankerDriverConfig
from ......utils.cache_kv.CacheOperations import CacheOperations


@dataclass
class KnowledgeComparatorConfig(BaseComponentConfig):
    """Конфигурация "Knowledge Comparator"-стадии QA-конвейера.
    :param reranker_driver_config: Конфигурация Retrieve/Rerank-оператора. Значение по умолчанию KC_RERANKDRIVER_DEFAULT_CONFIG.
    :type reranker_driver_config: Union[Dict,RerankerDriverConfig], optional
    :param max_k: Максимальное количество вершин из графа знаний, которое может быть сопоставлено одной сущности. Значение по умолчанию 1.
    :type max_k: int, optional
    :param k_compare: Служебный гиперпараметр. Значение по умолчанию 5.
    :type k_compare: int, optional
    :param cache_table_name: Название таблицы в структуре (базе) данных, куда будут сохраняться (кешироваться) основные результаты работы KnowledgeComparator-класса. Значение по умолчанию 'qa_kcomparator_stage_cache'.
    :type cache_table_name: str, optional
    """
    reranker_driver_config: Union[Dict, RerankerDriverConfig] = field(default_factory=lambda: KC_RERANKDRIVER_DEFAULT_CONFIG)
    max_k: int = 1
    k_compare: int = 5

    cache_table_name: str = 'qa_kcomparator_stage_cache'
    log: Logger = field(default_factory=lambda: Logger(KC_MAIN_LOG_PATH))

    def to_str(self):
        return f"{self.reranker_driver_config.to_str()};{self.max_k}:{self.k_compare}"

    @staticmethod
    def from_dict(dict_config: Dict):
        dictconfig_copy = deepcopy(dict_config)
        formated_config = KnowledgeComparatorConfig(**dictconfig_copy)
        formated_config.formate_fields()
        return formated_config

    def formate_fields(self):
        if isinstance(self.reranker_driver_config, dict):
            self.reranker_driver_config = RerankerDriverConfig.from_dict(self.reranker_driver_config)
        else:
            self.reranker_driver_config.formate_fields()


class KnowledgeComparator(CacheUtils, CacheOperations):
    """Верхнеуровневый класс второй стадии QA-конвейера для сопоставления информации из user-вопроса с имеющейся информацией в памяти (графе знаний) ассистента.

    :param kg_model: Модель памяти (графа знаний) ассистента.
    :type kg_model: KnowledgeGraphModel
    :param config: Конфигурация "Knowledge Comparator"-стадии. Значение по умолчанию KnowledgeComparatorConfig().
    :type config: Union[KnowledgeComparatorConfig,Dict], optional
    :param cache_kvdriver_config: Конфигурация структуры данных для кеширования промежуточных результатов в рамках компонент данного класса. Значение по умолчанию None.
    :type cache_kvdriver_config: Union[KeyValueDriverConfig, None], optional
    """

    def __init__(self, kg_model: KnowledgeGraphModel, config: Union[KnowledgeComparatorConfig, Dict] = KnowledgeComparatorConfig(),
                 cache_kvdriver_config: KeyValueDriverConfig = None) -> None:
        if isinstance(config, dict):
            config: KnowledgeComparatorConfig = KnowledgeComparatorConfig.from_dict(config)
        else:
            config.formate_fields()
        self.config = config

        self.kg_model = kg_model

        self.cachekv = self.init_cachekv(
            cache_kvdriver_config, config.cache_table_name)

        self.retriever = RerankerDriver.specify(
            self.config.reranker_driver_config,
            kg_model.graph_embeddings.nodes_vcomposers[NodeType.object])

        self.log = self.config.log
        self.verbose = self.config.verbose

    def get_cache_key(self, query_info: QueryInfo) -> List[object]:
        """Формирует ключ кэша для результата сопоставления сущностей с узлами графа.

        В ключ включается строковое представление конфигурации компаратора, сериализованное представление входного QueryInfo.

        :param query_info: Структура с исходным запросом и дополнительными полями.
        :type query_info: QueryInfo
        :return: Список строк, используемый как составной ключ кеша.
        :rtype: List[object]
        """
        return [self.config.to_str(), query_info.to_str()]

    @accumulate_step_info
    @CacheUtils.cache_method_output
    def link_kgnodes_to_query(self, query_info: QueryInfo) -> Tuple[Tuple[List[NodeInfo], List[object]], ReturnInfo]:
        """Метод предназначен для сопоставления (матчинга) сущностей, извлечённых из user-вопроса, с вершинами из графа знаний ассистента.

        :param query_structure: Структура данных, которая хранит user-вопрос и извлечённые из него сущности.
        :type query_structure: QueryInfo
        :return: Кортеж из двух объектов: (1) (список сопоставленных узлов, список имён/документов по сущностям); (2) статус завершения операции с пояснительной информацией.
        :rtype: Tuple[Tuple[List[NodeInfo], List[object]], ReturnInfo]
        """
        self.log("START MATCHING KEY WORDS ...", verbose=self.verbose)
        self.log(f"BASE_QUESTION ID: {create_id(query_info.query)}", verbose=self.verbose)
        self.log(f"BASE_QUESTION: {query_info.query}", verbose=self.verbose)
        self.log(f"ENTITIES: {query_info.entities}", verbose=self.verbose)

        rinfo = ReturnInfo()
        linked_nodes: List[NodeInfo] = []
        linked_nodes_by_entities = []

        for entity in query_info.entities:

            cur_linked_nodes: List[VectorDBInstance] = self.retriever.run(entity, top_k=self.config.max_k)
            linked_nodes += list(map(
                lambda node: NodeInfo(id=node.id, type=NodeType.object, text=node.document),
                cur_linked_nodes
            ))

            cur_documents = list(map(lambda item: item.document, cur_linked_nodes))
            cur_documents_lower = list(map(lambda document: document.lower(), cur_documents))
            if entity.lower() in cur_documents_lower[:self.config.k_compare]:
                cur_unique_names = [entity]
            else:
                cur_unique_names = [entity] + cur_documents[:self.config.max_k]
            linked_nodes_by_entities.append(cur_unique_names)

        if len(linked_nodes) == 0:
            rinfo.status = ReturnStatus.zero_linked_nodes
            rinfo.message = STATUS_MESSAGE[rinfo.status]
        else:
            self.log(f"RESULT: {len(linked_nodes)}", verbose=self.verbose)
            for i, node in enumerate(linked_nodes):
                self.log(f"{i}. {node}", verbose=self.verbose)

        self.log(f"STATUS: {STATUS_MESSAGE[rinfo.status]}", verbose=self.verbose)

        return (linked_nodes, linked_nodes_by_entities), rinfo
