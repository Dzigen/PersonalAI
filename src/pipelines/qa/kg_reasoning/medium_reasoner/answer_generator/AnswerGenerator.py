from dataclasses import dataclass, field
from typing import Tuple, Union, List, Dict

from .config import DEFAULT_ANSWCLS_TASK_CONFIG, DEFAULT_ANSWGEN_TASK_CONFIG, ANSWGEN_MAIN_LOG_PATH
from .utils import MediumAGeneratorTaskSolvers
from ......utils import ReturnInfo, Logger, AgentTaskSolverConfig, AgentTaskSolver
from ......utils.errors import ReturnStatus
from ......agents.utils import AbstractAgentConnector
from ......utils.data_structs import create_id, SearchPlanInfo, BaseComponentConfig, LanguageConfig
from ......db_drivers.kv_driver import KeyValueDriverConfig
from ......utils.cache_kv import CacheUtils
from ......utils.agent_stat_analyzer.AgentStatOperations import AgentStatOperations
from ......utils.cache_kv.CacheOperations import CacheOperations
from ......utils.agent_stat_analyzer import AgentStatAnalyzerConfig


@dataclass
class AnswerGeneratorConfig(BaseComponentConfig, LanguageConfig):
    """Конфигурация AnswerGenerator-стадии MediumQA-ризонера.

    :param agent_gen_stategy: Стратегия генерации текста для используемого LLM-агента. В случае None-значение будет использоваться стратегия по умолчанию. Значение по умолчанию None.
    :type agent_gen_stategy: Union[None,Dict[str, Union[str, int, float]]], optional
    :param answer_classifier_agent_task_config: Конфигурация атомарной задачи для LLM-агента по определению наличия необходимой информации для генерации релевантного ответа на вопрос. Значение по умолчанию DEFAULT_ANSWCLS_TASK_CONFIG.
    :type answer_classifier_agent_task_config: AgentTaskSolverConfig, optional
    :param answer_generator_agent_task_config: Конфигурация атомарной задачи для LLM-агента по выполнению условной генарции овтета на заданный user-вопрос. Значение по умолчанию DEFAULT_ANSWGEN_TASK_CONFIG.
    :type answer_generator_agent_task_config: AgentTaskSolverConfig, optional
    :param cache_table_name: Название таблицы в структуре (базе) данных, куда будут сохраняться (кешироваться) основные результаты работы ClueAnswersSummarizer-класса. Значение по умолчанию 'medreasn_answgen_main_stage_cache'.
    :type cache_table_name: str, optional
    """
    agent_gen_stategy: Union[None, Dict[str, Union[str, int, float]]] = None
    answer_classifier_agent_task_config: AgentTaskSolverConfig = field(
        default_factory=lambda: DEFAULT_ANSWCLS_TASK_CONFIG)
    answer_generator_agent_task_config: AgentTaskSolverConfig = field(
        default_factory=lambda: DEFAULT_ANSWGEN_TASK_CONFIG)

    cache_table_name: str = 'medreasn_answgen_main_stage_cache'
    log: Logger = field(default_factory=lambda: Logger(ANSWGEN_MAIN_LOG_PATH))

    def to_str(self):
        return f"{self.lang}|{self.agent_gen_stategy}|{self.answer_classifier_agent_task_config.version}|{self.answer_generator_agent_task_config.version}"


class AnswerGenerator(CacheUtils, CacheOperations, AgentStatOperations):
    """Верхнеуровневый класс стадии #4 MediumQA-конвейера для генерации ответа на user-вопрос на основе информации,
    извлечённой из графа знаний с помощью плана/последовательности поисковых запросов.

    :param agent: Коннектор к конкретному LLM-агенту для выполнения inference-операций.
    :type agent: AbstractAgentConnector
    :param config: Конфигурация AnswerGenerator-стадии. Значение по умолчанию AnswerGeneratorConfig().
    :type config:AnswerGeneratorConfig, optional
    :param cache_kvdriver_config: Конфигурация структуры данных для кеширования промежуточных результатов в рамках компонент данного класса. Значение по умолчанию None.
    :type cache_kvdriver_config: KeyValueDriverConfig, optional
    :param inferencestat_config: Конфигурация компоненты для сбора информации и расчёта статистик по результатам выполнения inference-операциий в рамках LLM-задач. Значение по умолчанию None.
    :type inferencestat_config: Union[None, AgentStatAnalyzerConfig], optional
    :param cache_llm_inference: Если True, то все результаты решения атомарных LLM-задач будут кешироваться, иначе False. Значение по умолчанию True.
    :type cache_llm_inference: bool, optional
    """

    def __init__(self, agent: AbstractAgentConnector, config: AnswerGeneratorConfig = AnswerGeneratorConfig(),
                 cache_kvdriver_config: Union[None, KeyValueDriverConfig] = None, cache_llm_inference: bool = True,
                 inferencestat_config: Union[None, AgentStatAnalyzerConfig] = None):
        self.config = config

        self.cachekv = self.init_cachekv(
            cache_kvdriver_config, config.cache_table_name)

        self.agent = agent
        agents_cache_config = None
        if cache_llm_inference:
            agents_cache_config = cache_kvdriver_config

        self.tasks_solvers: MediumAGeneratorTaskSolvers = MediumAGeneratorTaskSolvers(
            answer_classify_solver=AgentTaskSolver(
                self.agent, self.config.answer_classifier_agent_task_config, agents_cache_config, inferencestat_config),
            answer_gen_solver=AgentTaskSolver(
                self.agent, self.config.answer_generator_agent_task_config, agents_cache_config, inferencestat_config)
        )

        self.log = self.config.log
        self.verbose = self.config.verbose

    def get_cache_key(self, search_plan: SearchPlanInfo) -> List[str]:
        str_using_agent_info = f"{self.agent.CONNECTOR_KW}:{self.agent.config.to_str()}"
        return [search_plan.to_str(), self.config.to_str(), str_using_agent_info]

    @CacheUtils.cache_method_output
    def perform(self, search_plan: SearchPlanInfo) -> Tuple[Union[None, str], ReturnInfo]:
        """Метод предназначен для генерации ответа на user-вопрос на основе результатов (извлечённой из графа знаний информации),
        полученных в рамках выполнной последовательности поисковых запросов (шагов плана поиска). Если на основе имеющейся информации
        нельзя сгенерировать релевантный ответ на user-вопрос, то возвращается None.

        :param search_plan: Структура данных, хранящая план поиска с промежуточными и доп. результатами.
        :type search_plan: SearchPlanInfo
        :return: Кортеж из двух объектов: (1) Ответ на user-вопрос; (2) статус завершения операции с пояснительной информацией.
        :rtype: Tuple[str, ReturnInfo]
        """
        self.log("START ANSWER-TRYING...", verbose=self.config.verbose)
        self.log(
            f"QUERY ID: {create_id(search_plan.base_query)}", verbose=self.config.verbose)
        self.log(f"CURRENT PLAN: {search_plan}", verbose=self.config.verbose)
        answer, info = None, ReturnInfo()

        self.log("Выполняем проверку на возможность генерации релевантного ответа...",
                 verbose=self.verbose)
        can_answer, status = self.tasks_solvers.answer_classify_solver.solve(
            lang=self.config.lang, gen_strategy=self.config.agent_gen_stategy,
            search_plan=search_plan)
        self.log(f"RESULT: {can_answer}", verbose=self.config.verbose)

        if status == ReturnStatus.success:
            if can_answer:
                self.log("Выполняем генерацию ответа...", verbose=self.verbose)
                answer, status = self.tasks_solvers.answer_gen_solver.solve(
                    lang=self.config.lang, gen_strategy=self.config.agent_gen_stategy,
                    search_plan=search_plan)
                self.log(f"RESULT: {answer}", verbose=self.config.verbose)

            else:
                self.log(
                    "На основании информации, полученной по текущему плану нельзя сгенерировать релевантный ответ.", verbose=self.verbose)

        info.status = status
        self.log(f"STATUS: {info.status}", verbose=self.config.verbose)

        return answer, info
