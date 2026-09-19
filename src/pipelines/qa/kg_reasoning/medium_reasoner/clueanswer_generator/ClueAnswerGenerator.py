from dataclasses import dataclass, field
from typing import Tuple, Union, List, Dict
import hashlib
from copy import deepcopy

from .config import CAGEN_MAIN_LOG_PATH
from .utils import MediumCAGeneratorTaskSolvers, ClueAnswerGeneratorAgentTasksConfig
from ......utils.errors import STATUS_MESSAGE
from ......utils import ReturnInfo, Logger, AgentTaskSolver, accumulate_stage_info, \
    CompositeModuleDetailedResult, ModuleType
from ......agents.utils import AbstractAgentConnector
from ......utils.data_structs import create_id, Triplet, TripletCreator, BaseComponentConfig, LanguageConfig
from ......db_drivers.kv_driver import KeyValueDriverConfig
from ......utils.cache_kv import CacheUtils
from ......utils import ReturnStatus
from ......utils.agent_stat_analyzer import AgentStatAnalyzerConfig
from ......utils.agent_stat_analyzer.AgentStatOperations import AgentStatOperations
from ......utils.cache_kv.CacheOperations import CacheOperations


@dataclass
class ClueAnswerGeneratorConfig(BaseComponentConfig, LanguageConfig):
    """Конфигурация ClueAnswerGenerator-стадии MediumQA-ризонера.

    :param agent_gen_stategy: Стратегия генерации текста для используемого LLM-агента. В случае None-значения будет использоваться стратегия по умолчанию. Значение по умолчанию None.
    :type agent_gen_stategy: Union[None,Dict[str, Union[str, int, float]]], optional
    :param agent_tasks_config: Конфигурации LLM-промптов для решения заданных задач с помощью LLM-агента. Значение по умолчанию ClueAnswerGeneratorAgentTasksConfig().
    :type agent_tasks_config: Union[ClueAnswerGeneratorAgentTasksConfig, Dict], optional
    :param cache_table_name: Название таблицы в структуре (базе) данных, куда будут сохраняться (кешироваться) основные результаты работы ClueAnswersSummarizer-класса. Значение по умолчанию 'medreasn_cagen_main_stage_cache'.
    :type cache_table_name: str, optional
    """
    lang: str = 'auto'
    agent_gen_stategy: Union[None, Dict[str, Union[str, int, float]]] = None
    agent_tasks_config: Union[ClueAnswerGeneratorAgentTasksConfig, Dict] = field(default_factory=lambda: ClueAnswerGeneratorAgentTasksConfig())

    cache_table_name: str = 'medreasn_cagen_main_stage_cache'
    log_path: str = CAGEN_MAIN_LOG_PATH

    def to_str(self):
        return f"{self.lang}|{self.agent_gen_stategy}|{self.agent_tasks_config.to_str()}"

    @staticmethod
    def from_dict(dict_config: Dict):
        dictconfig_copy = deepcopy(dict_config)
        formated_config = ClueAnswerGeneratorConfig(**dictconfig_copy)
        formated_config.formate_fields()
        return formated_config

    def formate_fields(self):
        if isinstance(self.agent_tasks_config, dict):
            self.agent_tasks_config = ClueAnswerGeneratorAgentTasksConfig.from_dict(self.agent_tasks_config)


class ClueAnswerGenerator(CacheUtils, CacheOperations, AgentStatOperations):
    """Верхнеуровневый класс стадии #3.1.2 MediumQA-конвейера для суммаризации/резюмирования информации, извлечённой из графа знаний (памяти ассистента) по clue-запросу.

    :param agent: Коннектор к конкретному LLM-агенту для выполнения inference-операций.
    :type agent: AbstractAgentConnector
    :param config: Конфигурация ClueAnswerGenerator-стадии. Значение по умолчанию ClueAnswerGeneratorConfig().
    :type config: Union[ClueAnswerGeneratorConfig,Dict], optional
    :param cache_kvdriver_config: Конфигурация структуры данных для кеширования промежуточных результатов в рамках компонент данного класса. Значение по умолчанию None.
    :type cache_kvdriver_config: KeyValueDriverConfig, optional
    :param inferencestat_config: Конфигурация компоненты для сбора информации и расчёта статистик по результатам выполнения inference-операций в рамках LLM-задач. Значение по умолчанию None.
    :type inferencestat_config: Union[None, AgentStatAnalyzerConfig], optional
    :param cache_llm_inference: Если True, то все результаты решения атомарных LLM-задач будут кешироваться, иначе False. Значение по умолчанию True.
    :type cache_llm_inference: bool, optional
    """

    def __init__(self, agent: AbstractAgentConnector, config: Union[ClueAnswerGeneratorConfig, Dict] = ClueAnswerGeneratorConfig(),
                 cache_kvdriver_config: Union[None, KeyValueDriverConfig] = None,
                 inferencestat_config: Union[None, AgentStatAnalyzerConfig] = None,
                 cache_llm_inference: bool = True,) -> None:
        if isinstance(config, dict):
            config: ClueAnswerGeneratorConfig = ClueAnswerGeneratorConfig.from_dict(config)
        else:
            config.formate_fields()
        self.config = config
        self.config.agent_tasks_config.versions_to_configs(self.config.verbose, self.config.log_level)

        self.cachekv = self.init_cachekv(
            cache_kvdriver_config, config.cache_table_name)

        self.agent = agent
        agents_cache_config = None
        if cache_llm_inference:
            agents_cache_config = cache_kvdriver_config

        self.tasks_solvers: MediumCAGeneratorTaskSolvers = MediumCAGeneratorTaskSolvers(
            cagen_solver=AgentTaskSolver(
                self.agent, self.config.agent_tasks_config.cagen, agents_cache_config, inferencestat_config)
        )

        self.log = Logger(config.log_path)
        self.verbose = self.config.verbose
        self.log_level = self.config.log_level

    def get_cache_key(self, query: str, context_triplets: List[Triplet]) -> List[str]:
        str_triplets = hashlib.sha1("\n".join(sorted([TripletCreator.stringify(
            triplet)[1] for triplet in context_triplets])).encode()).hexdigest()
        str_using_agent_info = f"{self.agent.CONNECTOR_KW}:{self.agent.config.to_str()}"
        return [self.config.to_str(), query, str_triplets, str_using_agent_info]

    @accumulate_stage_info
    @CacheUtils.cache_method_output
    def perform(self, query: str, context_triplets: List[Triplet]) -> Tuple[str, ReturnInfo, CompositeModuleDetailedResult]:
        """Метод предназначен для генерации clue-ответа на clue-запрос, на основе информации, извлечённой из графа знаний.

        :param query: Clue-запрос на естественном языке.
        :type query: str
        :param context_triplets: Набор релевантной информации (в виде триплетов), извлечённой по заданному clue-запросу.
        :type context_triplets: List[Triplet]
        :return: Кортеж из трёх объектов: (1) Резюмированный/сформированный ответ на clue-запрос; (2) статус завершения операции с пояснительной информацией; (3) структура данных с промежуточными результатами реботы метода.
        :rtype: Tuple[str, ReturnInfo, CompositeModuleDetailedResult]
        """
        self.log.debug("START CLUE-ANSWER GENRATION ...", verbose=self.verbose, log_level=self.log_level)
        self.log.debug("* Question hash: %s", create_id(query), verbose=self.verbose, log_level=self.log_level)
        self.log.debug("* Question: %s", query, verbose=self.verbose, log_level=self.log_level)

        self.log.debug("CONTEXT TRIPLES: %s", verbose=self.verbose, log_level=self.log_level)
        for triplet in context_triplets:
            self.log.debug("* [%s] %s", triplet.id, triplet, verbose=self.verbose, log_level=self.log_level)
        rinfo, module_trace = ReturnInfo(), CompositeModuleDetailedResult()

        self.log.debug("Выполнение условной генерации ответа на вопрос с помощью LLM-агента...", verbose=self.verbose, log_level=self.log_level)
        answer, status, trace = self.tasks_solvers.cagen_solver.solve(
            lang=self.config.lang, gen_strategy=self.config.agent_gen_stategy,
            query=query, triplets=context_triplets)
        module_trace.add("cagen_solver", ModuleType.task_solver, trace)

        if status != ReturnStatus.success:
            rinfo.occurred_warning.append(status)

        if answer is None or len(answer) == 0:
            rinfo.status = ReturnStatus.empty_answer
            rinfo.message = STATUS_MESSAGE[rinfo.status]

        self.log.debug("RESULT:\n* Generated answer: %s", answer, verbose=self.verbose, log_level=self.log_level)
        self.log.debug("STATUS: %s", rinfo.status, verbose=self.verbose, log_level=self.log_level)

        return answer, rinfo, module_trace
