from dataclasses import dataclass, field
from typing import Tuple, Union, List, Dict
from copy import deepcopy

from .config import ANSWGEN_MAIN_LOG_PATH
from .utils import MediumAGeneratorTaskSolvers, AnswerGeneratorAgentTasksConfig
from ..utils import RelInfoFoundBehaviour
from ......utils import ReturnInfo, Logger, AgentTaskSolver, accumulate_stage_info, \
    CompositeModuleDetailedResult, ModuleType
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

    :param agent_gen_stategy: Стратегия генерации текста для используемого LLM-агента. В случае None-значения будет использоваться стратегия по умолчанию. Значение по умолчанию None.
    :type agent_gen_stategy: Union[None,Dict[str, Union[str, int, float]]], optional
    :param agent_tasks_config: Конфигурации LLM-промптов для решения заданных задач с помощью LLM-агента. Значение по умолчанию AnswerGeneratorAgentTasksConfig().
    :type agent_tasks_config: Union[AnswerGeneratorAgentTasksConfig,Dict], optional
    :param cache_table_name: Название таблицы в структуре (базе) данных, куда будут сохраняться (кешироваться) основные результаты работы ClueAnswersSummarizer-класса. Значение по умолчанию 'medreasn_answgen_main_stage_cache'.
    :type cache_table_name: str, optional
    """
    agent_gen_stategy: Union[None, Dict[str, Union[str, int, float]]] = None
    agent_tasks_config: Union[Dict, AnswerGeneratorAgentTasksConfig] = field(default_factory=lambda: AnswerGeneratorAgentTasksConfig())

    cache_table_name: str = 'medreasn_answgen_main_stage_cache'
    log_path: str = ANSWGEN_MAIN_LOG_PATH

    def to_str(self):
        return f"{self.lang}|{self.agent_gen_stategy}|{self.agent_tasks_config.to_str()}"

    @staticmethod
    def from_dict(dict_config: Dict):
        dictconfig_copy = deepcopy(dict_config)
        formated_config = AnswerGeneratorConfig(**dictconfig_copy)
        formated_config.formate_fields()
        return formated_config

    def formate_fields(self):
        if isinstance(self.agent_tasks_config, dict):
            self.agent_tasks_config = AnswerGeneratorAgentTasksConfig.from_dict(self.agent_tasks_config)


class AnswerGenerator(CacheUtils, CacheOperations, AgentStatOperations):
    """Верхнеуровневый класс стадии #4 MediumQA-конвейера для генерации ответа на user-вопрос на основе информации,
    извлечённой из графа знаний с помощью плана/последовательности поисковых запросов.

    :param agent: Коннектор к конкретному LLM-агенту для выполнения inference-операций.
    :type agent: AbstractAgentConnector
    :param config: Конфигурация AnswerGenerator-стадии. Значение по умолчанию AnswerGeneratorConfig().
    :type config: Union[AnswerGeneratorConfig,Dict], optional
    :param cache_kvdriver_config: Конфигурация структуры данных для кеширования промежуточных результатов в рамках компонент данного класса. Значение по умолчанию None.
    :type cache_kvdriver_config: KeyValueDriverConfig, optional
    :param inferencestat_config: Конфигурация компоненты для сбора информации и расчёта статистик по результатам выполнения inference-операций в рамках LLM-задач. Значение по умолчанию None.
    :type inferencestat_config: Union[None, AgentStatAnalyzerConfig], optional
    :param cache_llm_inference: Если True, то все результаты решения атомарных LLM-задач будут кешироваться, иначе False. Значение по умолчанию True.
    :type cache_llm_inference: bool, optional
    """

    def __init__(self, agent: AbstractAgentConnector, config: Union[AnswerGeneratorConfig, Dict] = AnswerGeneratorConfig(),
                 cache_kvdriver_config: Union[None, KeyValueDriverConfig] = None, cache_llm_inference: bool = True,
                 inferencestat_config: Union[None, AgentStatAnalyzerConfig] = None):
        if isinstance(config, dict):
            config: AnswerGeneratorConfig = AnswerGeneratorConfig.from_dict(config)
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

        self.tasks_solvers: MediumAGeneratorTaskSolvers = MediumAGeneratorTaskSolvers(
            answer_classify_solver=AgentTaskSolver(
                self.agent, self.config.agent_tasks_config.answer_classifier, agents_cache_config, inferencestat_config),
            strict_answer_gen_solver=AgentTaskSolver(
                self.agent, self.config.agent_tasks_config.strict_answer_generator, agents_cache_config, inferencestat_config),
            casual_answer_gen_solver=AgentTaskSolver(
                self.agent, self.config.agent_tasks_config.casual_answer_generator, agents_cache_config, inferencestat_config)
        )

        self.log = Logger(config.log_path)
        self.verbose = self.config.verbose
        self.log_level = self.config.log_level

    def get_cache_key(self, search_plan: SearchPlanInfo, relinfo_found_behaviour: RelInfoFoundBehaviour) -> List[str]:
        str_using_agent_info = f"{self.agent.CONNECTOR_KW}:{self.agent.config.to_str()}"
        return [search_plan.to_str(), self.config.to_str(), str_using_agent_info]

    @accumulate_stage_info
    @CacheUtils.cache_method_output
    def perform(self, search_plan: SearchPlanInfo, relinfo_found_behaviour: RelInfoFoundBehaviour = RelInfoFoundBehaviour.casual_answer) -> Tuple[Union[None, str], ReturnInfo, CompositeModuleDetailedResult]:
        """Метод предназначен для генерации ответа на user-вопрос на основе результатов (извлечённой из графа знаний информации),
        полученных в рамках выполненной последовательности поисковых запросов (шагов плана поиска). Если на основе имеющейся информации
        нельзя сгенерировать релевантный ответ на user-вопрос, то возвращается None.

        :param search_plan: Структура данных, хранящая план поиска с промежуточными и доп. результатами.
        :type search_plan: SearchPlanInfo
        :param relinfo_found_behaviour: ... . Значение по умолчанию RelInfoFoundBehaviour.casual_answer.
        :type relinfo_found_behaviour: RelInfoFoundBehaviour
        :return: Кортеж из трёх объектов: (1) Ответ на user-вопрос; (2) статус завершения операции с пояснительной информацией; (3) структура данных с промежуточными результатами реботы метода.
        :rtype: Tuple[str, ReturnInfo, CompositeModuleDetailedResult]
        """
        self.log.debug("START ANSWER-TRYING...", verbose=self.verbose, log_level=self.log_level)
        self.log.debug("* Query hash: %s", create_id(search_plan.base_query), verbose=self.verbose, log_level=self.log_level)
        self.log.debug("* Current plan: %s", search_plan, verbose=self.verbose, log_level=self.log_level)
        answer, rinfo, module_trace = None, ReturnInfo(), CompositeModuleDetailedResult()

        self.log.debug("Выполняем проверку на возможность генерации релевантного ответа...", verbose=self.verbose, log_level=self.log_level)
        can_answer, status, trace = self.tasks_solvers.answer_classify_solver.solve(
            lang=self.config.lang, gen_strategy=self.config.agent_gen_stategy,
            search_plan=search_plan)
        module_trace.add("answer_classify_solver", ModuleType.task_solver, trace)
        self.log.debug("RESULT: %s", can_answer, verbose=self.verbose, log_level=self.log_level)

        if status == ReturnStatus.success:
            if can_answer:
                self.log.debug("Выполняем генерацию ответа...", verbose=self.verbose, log_level=self.log_level)
                if relinfo_found_behaviour == RelInfoFoundBehaviour.casual_answer:
                    answer, status, trace = self.tasks_solvers.casual_answer_gen_solver.solve(
                        lang=self.config.lang, gen_strategy=self.config.agent_gen_stategy, search_plan=search_plan)
                    module_trace.add("casual_answer_gen_solver", ModuleType.task_solver, trace)
                elif relinfo_found_behaviour == RelInfoFoundBehaviour.strict_answer:
                    answer, status, trace = self.tasks_solvers.strict_answer_gen_solver.solve(
                        lang=self.config.lang, gen_strategy=self.config.agent_gen_stategy, search_plan=search_plan)
                    module_trace.add("strict_answer_gen_solver", ModuleType.task_solver, trace)
                else:
                    raise ValueError(f"relinfo_found_behaviour: {relinfo_found_behaviour}")

                self.log.debug("RESULT: %s", answer, verbose=self.verbose, log_level=self.log_level)

            else:
                self.log.warning(
                    "На основании информации, полученной по текущему плану нельзя сгенерировать релевантный ответ.", verbose=self.verbose, log_level=self.log_level)

        rinfo.status = status
        self.log.debug("STATUS: %s", rinfo.status, verbose=self.verbose, log_level=self.log_level)

        return answer, rinfo, module_trace
