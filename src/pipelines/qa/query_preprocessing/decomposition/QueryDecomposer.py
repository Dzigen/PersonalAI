from dataclasses import dataclass, field
from typing import Tuple, List, Union, Dict
from copy import deepcopy

from .config import QD_MAIN_LOG_PATH
from .utils import QueryDecomposerTaskSolvers, QueryDecomposerAgentTasksConfig
from .....utils import accumulate_stage_info, CompositeModuleDetailedResult, ModuleType
from .....utils.cache_kv import CacheUtils
from .....utils.errors import STATUS_MESSAGE
from .....utils.data_structs import create_id, QueryPreprocessingInfo, BaseComponentConfig, LanguageConfig
from .....agents.utils import AbstractAgentConnector
from .....utils import ReturnInfo, Logger, ReturnStatus, AgentTaskSolver
from .....db_drivers.kv_driver import KeyValueDriverConfig
from .....utils.agent_stat_analyzer import AgentStatAnalyzerConfig
from .....utils.cache_kv.CacheOperations import CacheOperations
from .....utils.agent_stat_analyzer.AgentStatOperations import AgentStatOperations


@dataclass
class QueryDecomposerConfig(BaseComponentConfig, LanguageConfig):
    """Конфигурация QueryDecomposer-операции.

    :param agent_gen_stategy: Стратегия генерации текста для используемого LLM-агента. В случае None-значения будет использоваться стратегия по умолчанию. Значение по умолчанию None.
    :type agent_gen_stategy: Union[None,Dict[str, Union[str, int, float]]], optional
    :param agent_tasks_config: Конфигурации LLM-промптов для решения заданных задач с помощью LLM-агента. Значение по умолчанию QueryDecomposerAgentTasksConfig().
    :type agent_tasks_config: Union[Dict,QueryDecomposerAgentTasksConfig], optional
    :param cache_table_name: Название таблицы в структуре (базе) данных, куда будут сохраняться (кешироваться) основные результаты работы QueryDecomposer-класса. Значение по умолчанию 'qp_decomposition_stage_cache'.
    :type cache_table_name: str, optional
    """
    agent_gen_stategy: Union[None, Dict[str, Union[str, int, float]]] = None
    agent_tasks_config: Union[Dict, QueryDecomposerAgentTasksConfig] = field(default_factory=lambda: QueryDecomposerAgentTasksConfig())
    cache_table_name: str = 'qp_decomposition_stage_cache'
    log_path: str = QD_MAIN_LOG_PATH

    def to_str(self):
        return f"{self.lang}|{self.agent_gen_stategy}|{self.agent_tasks_config.to_str()}"

    @staticmethod
    def from_dict(dict_config: Dict):
        dictconfig_copy = deepcopy(dict_config)
        formated_config = QueryDecomposerConfig(**dictconfig_copy)
        formated_config.formate_fields()
        return formated_config

    def formate_fields(self):
        if isinstance(self.agent_tasks_config, dict):
            self.agent_tasks_config = QueryDecomposerAgentTasksConfig.from_dict(self.agent_tasks_config)


class QueryDecomposer(CacheUtils, CacheOperations, AgentStatOperations):
    """Класс, реализующий одну из операций по форматированию/предобработке user-вопроса в рамках QueryPreprocessor-стадии. Данный класс выполняет декомпозицию сложного/составного user-вопроса на независимые/простые под-вопросы.

    :param agent: Коннектор к конкретному LLM-агенту для выполнения inference-операций.
    :type agent: AbstractAgentConnector
    :param config: Конфигурация QueryDecomposer-операции. Значение по умолчанию QueryDecomposerConfig().
    :type config: Union[Dict,QueryDecomposerConfig], optional
    :param cache_kvdriver_config: Конфигурация структуры данных для кеширования промежуточных результатов в рамках компонент данного класса. Значение по умолчанию None.
    :type cache_kvdriver_config: KeyValueDriverConfig, optional
    :param inferencestat_config: Конфигурация компоненты для сбора информации и расчёта статистик по результатам выполнения inference-операций в рамках LLM-задач. Значение по умолчанию None.
    :type inferencestat_config: Union[None, AgentStatAnalyzerConfig], optional
    :param cache_llm_inference: Если True, то все результаты решения атомарных LLM-задач будут кешироваться, иначе False. Значение по умолчанию True.
    :type cache_llm_inference: bool, optional
    """

    def __init__(self, agent: AbstractAgentConnector, config: Union[Dict, QueryDecomposerConfig] = QueryDecomposerConfig(),
                 cache_kvdriver_config: KeyValueDriverConfig = None,
                 inferencestat_config: Union[None, AgentStatAnalyzerConfig] = None,
                 cache_llm_inference: bool = True):
        if isinstance(config, dict):
            config: QueryDecomposerConfig = QueryDecomposerConfig.from_dict(config)
        else:
            config.formate_fields()
        self.config = config
        self.config.agent_tasks_config.versions_to_configs(self.config.verbose, self.config.log_level)

        self.cachekv = self.init_cachekv(cache_kvdriver_config, config.cache_table_name)

        self.agent = agent
        agents_cache_config = None
        if cache_llm_inference:
            agents_cache_config = cache_kvdriver_config if cache_llm_inference else None

        self.tasks_solvers: QueryDecomposerTaskSolvers = QueryDecomposerTaskSolvers(
            decompose_classifier_solver=AgentTaskSolver(
                self.agent, self.config.agent_tasks_config.classify, agents_cache_config, inferencestat_config
            ),
            q_decomposition_solver=AgentTaskSolver(
                self.agent, self.config.agent_tasks_config.decompose, agents_cache_config, inferencestat_config
            )
        )

        self.log = Logger(self.config.log_path)
        self.verbose = self.config.verbose
        self.log_level = self.config.log_level

    def get_cache_key(self, query_info: QueryPreprocessingInfo) -> List[str]:
        """Формирует ключ кеша для результата декомпозиции.
        В ключ включаются строковое представление входной структуры QueryPreprocessingInfo, строковое представление конфигурации и идентификатор используемого LLM-агента.

        :param query_info: Класс с информацией о предобработанном запросе.
        :type query_info: QueryPreprocessingInfo
        :return: Список объектов, используемый как составной ключ кеша.
        :rtype: List[str]
        """
        str_using_agent_info = f"{self.agent.CONNECTOR_KW}:{self.agent.config.to_str()}"
        return [query_info.to_str(), self.config.to_str(), str_using_agent_info]

    @accumulate_stage_info
    @CacheUtils.cache_method_output
    def perform(self, query_info: QueryPreprocessingInfo) -> Tuple[List[str], ReturnInfo, CompositeModuleDetailedResult]:
        """Метод предназначен для выполнения операции форматирования/предобработки user-вопроса: декомпозиции сложных/составных user-вопросов на независимые/простые под-вопросы.

        :param query_info: Структура данных с результатами предыдущих операций предобработки/форматирования исходного user-вопроса.
        :type query_info: QueryPreprocessingInfo
        :return: Кортеж из трёх объектов: (1) список простых под-вопросов для исходного/сложного user-вопроса; (2) статус завершения операции с пояснительной информацией; (3) структура данных с промежуточными результатами реботы метода.
        :rtype: Tuple[List[str], ReturnInfo, CompositeModuleDetailedResult]
        """
        self.log.debug("START QUERY DECOMPOSITION...", verbose=self.verbose, log_level=self.log_level)
        self.log.debug("* Question hash: %s", create_id(query_info.base_query), verbose=self.verbose, log_level=self.log_level)
        self.log.debug("* Query info: %s", query_info, verbose=self.verbose, log_level=self.log_level)
        decomposed_query, rinfo = None, ReturnInfo()
        module_trace = CompositeModuleDetailedResult()

        if query_info.enchanced_query is not None:
            query = query_info.enchanced_query
        elif query_info.denoised_query is not None:
            query = query_info.denoised_query
        elif query_info.base_query is not None:
            query = query_info.base_query
        else:
            raise ValueError

        self.log.debug("Выполнение проверки на необходимость декомпозиции вопроса с помощью LLM-агента...", verbose=self.verbose, log_level=self.log_level)
        need_to_decompose, status, trace = self.tasks_solvers.decompose_classifier_solver.solve(
            lang=self.config.lang, gen_strategy=self.config.agent_gen_stategy, query=query)
        module_trace.add("decompose_classifier_solver", ModuleType.task_solver, trace)
        if status != ReturnStatus.success:
            rinfo.occurred_warning.append(status)

        if status == ReturnStatus.success:
            if need_to_decompose:
                self.log.debug("Выполнение разбиения вопроса на независимые под-вопросы с помощью LLM-агента...", verbose=self.verbose, log_level=self.log_level)
                decomposed_query, status, trace = self.tasks_solvers.q_decomposition_solver.solve(
                    lang=self.config.lang, gen_strategy=self.config.agent_gen_stategy, query=query)
                module_trace.add("q_decomposition_solver", ModuleType.task_solver, trace)
                if status != ReturnStatus.success:
                    rinfo.occurred_warning.append(status)
            else:
                self.log.debug("Выполнение декомпозиции вопроса не требуется", verbose=self.verbose, log_level=self.log_level)
                rinfo.occurred_warning.append(ReturnStatus.decompose_noneed)
                decomposed_query = [query]

        if decomposed_query is None:
            rinfo.status = ReturnStatus.empty_answer
            rinfo.message = STATUS_MESSAGE[rinfo.status]

        self.log.debug("RESULT: %s", decomposed_query, verbose=self.verbose, log_level=self.log_level)
        self.log.debug("STATUS: %s", rinfo.status, verbose=self.verbose, log_level=self.log_level)

        return decomposed_query, rinfo, module_trace
