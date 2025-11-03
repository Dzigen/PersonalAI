from dataclasses import dataclass, field
from typing import Tuple, List, Dict, Union, Dict
import json
from itertools import product

from .config import DEFAULT_CQGEN_TASK_CONFIG, CQGEN_MAIN_LOG_PATH
from .utils import MediumCQGeneratorTaskSolvers
from ......utils.data_structs import QueryInfo
from ......utils.errors import ReturnStatus
from ......utils import ReturnInfo, Logger, AgentTaskSolverConfig, AgentTaskSolver
from ......agents.utils import AbstractAgentConnector
from ......utils.data_structs import create_id, BaseComponentConfig, LanguageConfig, NodeInfo
from ......db_drivers.kv_driver import KeyValueDriverConfig
from ......db_drivers.vector_driver import VectorDBInstance
from ......utils.cache_kv import CacheUtils
from ......utils.agent_stat_analyzer import AgentStatAnalyzerConfig
from ......utils.cache_kv.CacheOperations import CacheOperations
from ......utils.agent_stat_analyzer.AgentStatOperations import AgentStatOperations


@dataclass
class ClueQueriesGeneratorConfig(BaseComponentConfig, LanguageConfig):
    """Конфигурация ClueQueriesGenerator-стадии MediumQA-ризонера.

    :param agent_gen_stategy: Стратегия генерации текста для используемого LLM-агента. В случае None-значение будет использоваться стратегия по умолчанию. Значение по умолчанию None.
    :type agent_gen_stategy: Union[None,Dict[str, Union[str, int, float]]], optional
    :param plan_initing_agent_task_config: Конфигурация атомарной задачи для LLM-агента по генерации clue-запросов. Значение по умолчанию DEFAULT_CQGEN_TASK_CONFIG.
    :type plan_initing_agent_task_config: AgentTaskSolverConfig, optional
    :param max_cqueries_amount: Максимальное количество clue-запросов, которое может быть сгенерировано. Значение по умолчанию 4.
    :type max_cqueries_amount: int, optional
    :param cache_table_name: Название таблицы в структуре (базе) данных, куда будут сохраняться (кешироваться) основные результаты работы ClueQueriesGenerator-класса. Значение по умолчанию 'medreasn_cquerygen_main_stage_cache'.
    :type cache_table_name: str, optional
    """
    agent_gen_stategy: Union[None, Dict[str, Union[str, int, float]]] = None
    cquerie_generator_agent_task_config: AgentTaskSolverConfig = field(
        default_factory=lambda: DEFAULT_CQGEN_TASK_CONFIG)
    max_cqueries_amount: int = 4

    cache_table_name: str = 'medreasn_cquerygen_main_stage_cache'
    log: Logger = field(default_factory=lambda: Logger(CQGEN_MAIN_LOG_PATH))

    def to_str(self):
        return f"{self.lang}|{self.agent_gen_stategy}|{self.cquerie_generator_agent_task_config.version}|{self.max_cqueries_amount}"


class ClueQueriesGenerator(CacheUtils, CacheOperations, AgentStatOperations):
    """Верхнеуровневый класс стадии #2.2 MediumQA-конвейера для генерации clue-запросов поиска на графе знаний.

    :param agent: Коннектор к конкретному LLM-агенту для выполнения inference-операций.
    :type agent: AbstractAgentConnector
    :param config: Конфигурация ClueQueriesGenerator-стадии. Значение по умолчанию ClueQueriesGeneratorConfig().
    :type config: ClueQueriesGeneratorConfig, optional
    :param cache_kvdriver_config: Конфигурация структуры данных для кеширования промежуточных результатов в рамках компонент данного класса. Значение по умолчанию None.
    :type cache_kvdriver_config: KeyValueDriverConfig, optional
    :param inferencestat_config: Конфигурация компоненты для сбора информации и расчёта статистик по результатам выполнения inference-операциий в рамках LLM-задач. Значение по умолчанию None.
    :type inferencestat_config: Union[None, AgentStatAnalyzerConfig], optional
    :param cache_llm_inference: Если True, то все результаты решения атомарных LLM-задач будут кешироваться, иначе False. Значение по умолчанию True.
    :type cache_llm_inference: bool, optional
    """

    def __init__(self, agent: AbstractAgentConnector, config: ClueQueriesGeneratorConfig = ClueQueriesGeneratorConfig(),
                 cache_kvdriver_config: KeyValueDriverConfig = None,
                 inferencestat_config: Union[None, AgentStatAnalyzerConfig] = None,
                 cache_llm_inference: bool = True):
        self.config = config

        self.cachekv = self.init_cachekv(
            cache_kvdriver_config, config.cache_table_name)

        self.agent = agent
        agents_cache_config = None
        if cache_llm_inference:
            agents_cache_config = cache_kvdriver_config

        self.tasks_solvers: MediumCQGeneratorTaskSolvers = MediumCQGeneratorTaskSolvers(
            cluequery_gen_solver=AgentTaskSolver(
                self.agent, self.config.cquerie_generator_agent_task_config, agents_cache_config, inferencestat_config)
        )

        self.log = self.config.log
        self.verbose = self.config.verbose

    def get_cache_key(self, search_query: str, matched_kg_objects: Dict[str, List[NodeInfo]]) -> List[object]:
        str_matchedobject = json.dumps({k: list(map(lambda vv: vv.text, v))
                                       for k, v in matched_kg_objects.items()}, ensure_ascii=False)
        str_using_agent_info = f"{self.agent.CONNECTOR_KW}:{self.agent.config.to_str()}"
        return [search_query, str_matchedobject, self.config.to_str(), str_using_agent_info]

    @CacheUtils.cache_method_output
    def perform(self, search_query: str, matched_kg_objects: Dict[str, List[NodeInfo]]) -> Tuple[List[QueryInfo], ReturnInfo]:
        """Метод предназначен для генерации/формирования clue-запросов к заданному шагу поиска (в рамках текущего плана).
        Clue-запросы генерируются по следующему алгоритму:
        (1) На основе matched_kg_objects-словаря формируется линейная комбинация сопоставленных вершин из графа знаний. Каждый sample
        представляет собой список конкретных вершин, который были сопоставлены (биекция / один к одному) сущностям из заданного базового запроса.
        (2) На основе базового запроса и каждого семпла с шага #1 (в отдельности) генерируются clue-запросы, которые заостряют внимание
        на поиск конкретной/детализированной (на сколько это возможно) информации.

        :param search_query: Базовый поисковый запрос на естественном языке (один из шагов поиска в рамках текущего плана).
        :type search_query: str
        :param matched_kg_objects: Набор сущностей их заданного поискового запроса, сопоставленный с релевантными вершинами из графа знаний.
        :type matched_kg_objects: Dict[str, List[NodeInfo]]
        :return: Кортеж из двух объектов: (1) список сформированных clue-запросов; (2) статус завершения операции с пояснительной информацией.
        :rtype: Tuple[List[QueryInfo], ReturnInfo]
        """
        self.log("START CLUE-QUERIES GENERATION...", verbose=self.config.verbose)
        self.log(f"SEARCH_QUERY ID: {create_id(search_query)}", verbose=self.config.verbose)
        self.log(f"SEARCH_QUERY: {search_query}", verbose=self.config.verbose)
        str_matchedobjects = ';'.join(
            [f'{k} - {[vv.text for vv in v]}' for k, v in matched_kg_objects.items()])
        self.log(f"MATCHED_KG_OBJECT: {str_matchedobjects}", verbose=self.config.verbose)
        clue_queries, info = [], ReturnInfo()
        unique_cqueries = set()

        if len(search_query) < 1 or len(matched_kg_objects) < 1:
            raise ValueError
        m_objects_amount = sum(
            list(map(lambda m_objects: len(m_objects), matched_kg_objects.values())))
        if m_objects_amount < 1:
            raise ValueError

        self.log(f"Получаем декартово произведение всех комбинаций объектов (по сущностям)...",
                 verbose=self.config.verbose)
        base_entities = sorted(list(filter(lambda entitie: len(
            matched_kg_objects[entitie]) > 0, matched_kg_objects.keys())))
        objects_groups = list(product(*[matched_kg_objects[k] for k in base_entities]))[:self.config.max_cqueries_amount]
        str_objectspermuts = ';'.join([f'[{k}] {len(v)}' for k, v in matched_kg_objects.items()])
        self.log(f"RESULT:\n- всего сущностей: {len(matched_kg_objects)}\n- после фильтрации: {len(base_entities)}\n- объектов для каждой сущности: {str_objectspermuts}\n- полученное количество комбинаций: {len(objects_groups)}", verbose=self.config.verbose)

        self.log("Генерируем clue-queries...", verbose=self.config.verbose)
        for i, cur_group in enumerate(objects_groups):
            self.log(f"Текущий cleu-query #: {i} / {len(objects_groups)}", verbose=self.config.verbose)
            formated_objects_group = list(map(lambda item: item.text, cur_group))

            self.log("Выполняем генерацию clue-query с помощью LLM-агента...", verbose=self.config.verbose)
            cur_cluequery, status = self.tasks_solvers.cluequery_gen_solver.solve(
                lang=self.config.lang, gen_strategy=self.config.agent_gen_stategy,
                query=search_query, base_entities=base_entities, matched_objects=formated_objects_group)
            self.log(f"RESULT: {cur_cluequery}", verbose=self.verbose)

            if status != ReturnStatus.success:
                info.status = status
                break
            else:
                if cur_cluequery in unique_cqueries:
                    self.log(
                        "Сгенерированное clue-query уже было получено ранее. Отбрасываем.", verbose=self.config.verbose)
                    continue
                else:
                    self.log(
                        "Сгенерированое clue-query ещё получено не было. Сохраняем.", verbose=self.config.verbose)
                    unique_cqueries.add(cur_cluequery)
                    clue_queries.append(QueryInfo(
                        query=cur_cluequery, entities=base_entities, linked_nodes=list(cur_group),
                        linked_nodes_by_entities=list(map(lambda pair: [base_entities[pair[0]], pair[1]], enumerate(formated_objects_group)))))

        self.log(
            f"RESULT:\n- Количество clue-queries после фильтрации по строкоовму представлению: {len(clue_queries)}", verbose=self.verbose)
        self.log(f"STATUS: {info.status}", verbose=self.verbose)

        return clue_queries, info
