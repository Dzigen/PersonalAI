from dataclasses import dataclass, field
from typing import Tuple, Union, List, Dict
from copy import deepcopy

from .config import PLANENH_MAIN_LOG_PATH
from .utils import MediumPlanEnhancerTaskSolvers, SearchPlanEnhancerAgentTasksConfig
from ......utils import ReturnInfo, Logger, AgentTaskSolverConfig, AgentTaskSolver, accumulate_stage_info, \
    CompositeModuleDetailedResult, ModuleType, CompositeModuleResult
from ......utils.errors import ReturnStatus
from ......agents.utils import AbstractAgentConnector
from ......utils.data_structs import create_id, SearchPlanInfo, BaseComponentConfig, LanguageConfig
from ......db_drivers.kv_driver import KeyValueDriverConfig
from ......utils.cache_kv import CacheUtils
from ......utils.agent_stat_analyzer import AgentStatAnalyzerConfig
from ......utils.cache_kv.CacheOperations import CacheOperations
from ......utils.agent_stat_analyzer.AgentStatOperations import AgentStatOperations


@dataclass
class SearchPlanEnhancerConfig(BaseComponentConfig, LanguageConfig):
    """Конфигурация SearchPlanEnhancer-стадии MediumQA-ризонера.

    :param plan_enhancment: Если True, то невыполненные шаги аходящего план поиска будут скорректированы (перегенерированы на основании информации, полученной с предыдущих шагов), иначе False (план возврашается без изменений). Значение по умолчанию True.
    :type plan_enhancment: bool, optional
    :param enable_enhance_classifier: ... . Значение по умолчанию False.
    :type enable_enhance_classifier: bool, optional
    :param agent_gen_stategy: Стратегия генерации текста для используемого LLM-агента. В случае None-значение будет использоваться стратегия по умолчанию. Значение по умолчанию None.
    :type agent_gen_stategy: Union[None,Dict[str, Union[str, int, float]]], optional
    :param agent_tasks_config: Конфигурации LLM-промптом для решения заданных задач с помощью LLM-агента. Значение по умолчанию SearchPlanEnhancerAgentTasksConfig().
    :type agent_tasks_config: Union[SearchPlanEnhancerAgentTasksConfig, Dict], optional
    :param cache_table_name: Название таблицы в структуре (базе) данных, куда будут сохраняться (кешироваться) основные результаты работы SearchPlanEnhancer-класса. Значение по умолчанию 'medreasn_planenh_main_stage_cache'.
    :type cache_table_name: str, optional
    """
    plan_enhancment: bool = True
    enable_enhance_classifier: bool = False
    agent_gen_stategy: Union[None, Dict[str, Union[str, int, float]]] = None
    agent_tasks_config: Union[SearchPlanEnhancerAgentTasksConfig, Dict] = field(default_factory=lambda: SearchPlanEnhancerAgentTasksConfig())

    cache_table_name: str = 'medreasn_planenh_main_stage_cache'
    log_path: str = PLANENH_MAIN_LOG_PATH

    def to_str(self):
        return f"{self.lang}|{self.agent_gen_stategy}|{self.agent_tasks_config.to_str()}|{self.plan_enhancment}|{self.enable_enhance_classifier}"

    @staticmethod
    def from_dict(dict_config: Dict):
        dictconfig_copy = deepcopy(dict_config)
        formated_config = SearchPlanEnhancerConfig(**dictconfig_copy)
        formated_config.formate_fields()
        return formated_config

    def formate_fields(self):
        if isinstance(self.agent_tasks_config, dict):
            self.agent_tasks_config = SearchPlanEnhancerAgentTasksConfig.from_dict(self.agent_tasks_config)


class SearchPlanEnhancer(CacheUtils, CacheOperations, AgentStatOperations):
    """Верхнеуровневый класс стадии #1 medium QA-конвейера для выполнения генерации/модификации плана поиска/извлечения информации из графа знаний.

    :param agent: Коннектор к конкретному LLM-агенту для выполнения inference-операций.
    :type agent: AbstractAgentConnector
    :param config: Конфигурация SearchPlanEnhancer-стадии. Значение по умолчанию SearchPlanEnhancerConfig().
    :type config: Union[SearchPlanEnhancerConfig,Dict], optional
    :param cache_kvdriver_config: Конфигурация структуры данных для кеширования промежуточных результатов в рамках компонент данного класса. Значение по умолчению None.
    :type cache_kvdriver_config: Union[KeyValueDriverConfig, None], optional
    :param inferencestat_config: Конфигурация компоненты для сбора информации и расчёта статистик по результатам выполнения inference-операциий в рамках LLM-задач. Значение по умолчанию None.
    :type inferencestat_config: Union[None, AgentStatAnalyzerConfig], optional
    :param cache_llm_inference: Если True, то все результаты решения атомарных LLM-задач будут кешироваться, иначе False. Значение по умолчанию True.
    :type cache_llm_inference: bool, optional
    """

    def __init__(self, agent: AbstractAgentConnector, config: Union[SearchPlanEnhancerConfig, Dict] = SearchPlanEnhancerConfig(),
                 cache_kvdriver_config: Union[None, KeyValueDriverConfig] = None,
                 inferencestat_config: Union[None, AgentStatAnalyzerConfig] = None,
                 cache_llm_inference: bool = True):
        if isinstance(config, dict):
            config: SearchPlanEnhancerConfig = SearchPlanEnhancerConfig.from_dict(config)
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

        self.tasks_solvers: MediumPlanEnhancerTaskSolvers = MediumPlanEnhancerTaskSolvers(
            plan_initialing_solver=AgentTaskSolver(
                self.agent, self.config.agent_tasks_config.plan_initing,
                agents_cache_config, inferencestat_config),
            enhance_classify_solver=AgentTaskSolver(
                self.agent, self.config.agent_tasks_config.enhance_classifier,
                agents_cache_config, inferencestat_config),
            plan_enhancing_solver=AgentTaskSolver(
                self.agent, self.config.agent_tasks_config.plan_enhancing,
                agents_cache_config, inferencestat_config),
            searchstop_classify_solver=AgentTaskSolver(
                self.agent, self.config.agent_tasks_config.searchstop_classifier,
                agents_cache_config, inferencestat_config)
        )

        self.log = Logger(config.log_path)
        self.verbose = self.config.verbose
        self.log_level = self.config.log_level

    def get_cache_key(self, search_step: int, search_plan: SearchPlanInfo) -> List[str]:
        str_using_agent_info = f"{self.agent.CONNECTOR_KW}:{self.agent.config.to_str()}"
        return [str(search_step), search_plan.to_str(), self.config.to_str(), str_using_agent_info]

    @accumulate_stage_info
    @CacheUtils.cache_method_output
    def perform(self, search_step: int, search_plan: SearchPlanInfo) -> Tuple[SearchPlanInfo, ReturnInfo, CompositeModuleDetailedResult]:
        """Метод предназначен для генерации/модификации плана поиска. Если шаг поиска равен нулю, то план генерируется с нуля,
        иначе выполняется проверка: необходимо перегенерировать не пройденные шаги или нет. Если перегенерация необходима,
        то выполняется соответствеющая операция, иначе план оставляется без изменений.

        :param search_step: Значение текущего шага поиска.
        :type search_step: int
        :param search_plan: Структура данных, хранящая план поиска с промежуточными и доп. результатами.
        :type search_plan: SearchPlanInfo
        :return: Кортеж из трёх объектов: (1) Модифицированный план поиска; (2) статус завершения операции с пояснительной информацией; (3) структура данных с промежуточными результатами реботы метода.
        :rtype: Tuple[SearchPlanInfo, ReturnInfo, CompositeModuleDetailedResult]
        """
        self.log.debug("START SEARCH-PLAN INITING/ENHANCING...", verbose=self.verbose, log_level=self.log_level)
        self.log.debug("* Query hash: %s", create_id(search_plan.base_query), verbose=self.verbose, log_level=self.log_level)
        self.log.debug("* Current plan: %s", search_plan, verbose=self.verbose, log_level=self.log_level)
        enhanced_search_plan, rinfo, module_trace = None, ReturnInfo(), CompositeModuleDetailedResult()

        if search_step < 0:
            raise ValueError(f"search_step: {search_step}")

        if search_step == 0:
            self.log.debug("Генерируем план поиска с нуля...", verbose=self.verbose, log_level=self.log_level)
            new_search_steps, rinfo.status, trace = self.tasks_solvers.plan_initialing_solver.solve(
                lang=self.config.lang, gen_strategy=self.config.agent_gen_stategy, query=search_plan.base_query)
            module_trace.add("plan_initialing_solver", ModuleType.task_solver, trace)

            if rinfo.status == ReturnStatus.success:
                str_searchplan = "\n".join([f'{i}. {gen_step}' for i, gen_step in enumerate(new_search_steps)])
                self.log.debug("RESULT: %d\n%s", len(new_search_steps), str_searchplan, verbose=self.verbose, log_level=self.log_level)

                enhanced_search_plan = deepcopy(search_plan)
                enhanced_search_plan.search_steps = new_search_steps
                enhanced_search_plan.steps_answers = []
            else:
                self.log.debug("RESULT: -1\n%s", new_search_steps, verbose=self.verbose, log_level=self.log_level)

        elif self.config.plan_enhancment:
            self.log.debug("Выполняем проверку на необходимость улучшения следующих шагов поиска в плане...", verbose=self.verbose, log_level=self.log_level)
            if self.config.enable_enhance_classifier:
                need_enhance, rinfo.status, trace = self.tasks_solvers.enhance_classify_solver.solve(
                    lang=self.config.lang, gen_strategy=self.config.agent_gen_stategy, query=search_plan.base_query,
                    search_steps=search_plan.search_steps, steps_answers=search_plan.steps_answers[:search_step])
                module_trace.add("enhance_classify_solver", ModuleType.task_solver, trace)
                self.log.debug("RESULT: %s", need_enhance, verbose=self.verbose, log_level=self.log_level)
            else:
                self.log.warning("Current step is disabled. Continue.", verbose=self.verbose, log_level=self.log_level)
                need_enhance = True

            if rinfo.status == ReturnStatus.success:
                if need_enhance:
                    self.log.debug("Улучшаем следующие шаги поиска в плане...", verbose=self.verbose, log_level=self.log_level)
                    enhanced_steps, rinfo.status, trace = self.tasks_solvers.plan_enhancing_solver.solve(
                        lang=self.config.lang, gen_strategy=self.config.agent_gen_stategy, query=search_plan.base_query,
                        search_steps=search_plan.search_steps, steps_answers=search_plan.steps_answers[:search_step])
                    module_trace.add("plan_enhancing_solver", ModuleType.task_solver, trace)

                    if rinfo.status == ReturnStatus.success:
                        str_enhancedsteps = "\n".join([f'{i}. {gen_step}' for i, gen_step in enumerate(enhanced_steps)])
                        self.log.debug("RESULT: %d\n%s", len(enhanced_steps), str_enhancedsteps, verbose=self.verbose, log_level=self.log_level)

                        enhanced_search_plan = deepcopy(search_plan)
                        enhanced_search_plan.search_steps = search_plan.search_steps[:search_step] + enhanced_steps
                        enhanced_search_plan.steps_answers = search_plan.steps_answers[:search_step]
                    else:
                        self.log.warning("RESULT: -1\n%s", enhanced_steps, verbose=self.verbose, log_level=self.log_level)

                else:
                    self.log.debug("Улучшение шагов поиска не требуется...", verbose=self.verbose, log_level=self.log_level)
                    enhanced_search_plan = deepcopy(search_plan)
        else:
            self.log.debug("Оператор корректировки существующего плана поиска выключен. Возвращается исходный план.", verbose=self.verbose, log_level=self.log_level)
            enhanced_search_plan = deepcopy(search_plan)
            rinfo.status = ReturnStatus.success

        self.log.debug("STATUS: %s", rinfo.status, verbose=self.verbose, log_level=self.log_level)

        return enhanced_search_plan, rinfo, module_trace
