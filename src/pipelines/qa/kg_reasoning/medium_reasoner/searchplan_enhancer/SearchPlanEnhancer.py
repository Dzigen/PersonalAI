from dataclasses import dataclass, field
from typing import Tuple, Union, List, Dict
from copy import deepcopy

from .config import PLANENH_MAIN_LOG_PATH
from .utils import MediumPlanEnhancerTaskSolvers, SearchPlanEnhancerAgentTasksConfig
from ......utils import ReturnInfo, Logger, AgentTaskSolverConfig, AgentTaskSolver
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

    :param agent_gen_stategy: Стратегия генерации текста для используемого LLM-агента. В случае None-значение будет использоваться стратегия по умолчанию. Значение по умолчанию None.
    :type agent_gen_stategy: Union[None,Dict[str, Union[str, int, float]]], optional
    :param agent_tasks_config: Конфигурации LLM-промптом для решения заданных задач с помощью LLM-агента. Значение по умолчанию SearchPlanEnhancerAgentTasksConfig().
    :type agent_tasks_config: Union[SearchPlanEnhancerAgentTasksConfig, Dict], optional
    :param cache_table_name: Название таблицы в структуре (базе) данных, куда будут сохраняться (кешироваться) основные результаты работы SearchPlanEnhancer-класса. Значение по умолчанию 'medreasn_planenh_main_stage_cache'.
    :type cache_table_name: str, optional
    """
    agent_gen_stategy: Union[None, Dict[str, Union[str, int, float]]] = None
    agent_tasks_config: Union[SearchPlanEnhancerAgentTasksConfig, Dict] = field(default_factory=lambda: SearchPlanEnhancerAgentTasksConfig())

    cache_table_name: str = 'medreasn_planenh_main_stage_cache'
    log: Logger = field(default_factory=lambda: Logger(PLANENH_MAIN_LOG_PATH))

    def to_str(self):
        return f"{self.lang}|{self.agent_gen_stategy}|{self.agent_tasks_config.to_str()}"

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
        self.config.agent_tasks_config.versions_to_configs()

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
                agents_cache_config, inferencestat_config)
        )

        self.log = self.config.log
        self.verbose = self.config.verbose

    def get_cache_key(self, search_step: int, search_plan: SearchPlanInfo) -> List[str]:
        str_using_agent_info = f"{self.agent.CONNECTOR_KW}:{self.agent.config.to_str()}"
        return [str(search_step), search_plan.to_str(), self.config.to_str(), str_using_agent_info]

    @CacheUtils.cache_method_output
    def perform(self, search_step: int, search_plan: SearchPlanInfo) -> Tuple[SearchPlanInfo, ReturnInfo]:
        """Метод предназначен для генерации/модификации плана поиска. Если шаг поиска равен нулю, то план генерируется с нуля,
        иначе выполняется проверка: необходимо перегенерировать не пройденные шаги или нет. Если перегенерация необходима,
        то выполняется соответствеющая операция, иначе план оставляется без изменений.

        :param search_step: Значение текущего шага поиска.
        :type search_step: int
        :param search_plan: Структура данных, хранящая план поиска с промежуточными и доп. результатами.
        :type search_plan: SearchPlanInfo
        :return: Кортеж из двух объектов: (1) Модифиицированный план поиска; (2) статус завершения операции с пояснительной информацией.
        :rtype: Tuple[SearchPlanInfo, ReturnInfo]
        """
        self.log("START SEARCH-PLAN INITING/ENHANCING...", verbose=self.verbose)
        self.log(f"QUERY ID: {create_id(search_plan.base_query)}", verbose=self.verbose)
        self.log(f"CURRENT PLAN: {search_plan}", verbose=self.verbose)
        enhanced_search_plan, rinfo = None, ReturnInfo()

        if search_step < 0:
            raise ValueError

        if search_step == 0:
            self.log("Генерируем план поиска с нуля...", verbose=self.verbose)
            new_search_steps, status = self.tasks_solvers.plan_initialing_solver.solve(
                lang=self.config.lang, gen_strategy=self.config.agent_gen_stategy, query=search_plan.base_query)
            str_searchplan = "\n".join(
                [f'{i}. {gen_step}' for i, gen_step in enumerate(new_search_steps)])
            self.log(
                f"RESULT: {len(new_search_steps)}\n{str_searchplan}", verbose=self.verbose)

            if status == ReturnStatus.success:
                enhanced_search_plan = deepcopy(search_plan)
                enhanced_search_plan.search_steps = new_search_steps
                enhanced_search_plan.steps_answers = []
        else:
            self.log(
                "Выполняем проверку на необходимость улучшения следующих шагов поиска в плане...", verbose=self.verbose)
            need_enhance, status = self.tasks_solvers.enhance_classify_solver.solve(
                lang=self.config.lang, gen_strategy=self.config.agent_gen_stategy, query=search_plan.base_query,
                search_steps=search_plan.search_steps, steps_answers=search_plan.steps_answers[:search_step])
            self.log(f"RESULT: {need_enhance}", verbose=self.verbose)

            if status == ReturnStatus.success:
                if need_enhance:
                    self.log("Улучшаем следующие шаги поиска в плане...",
                             verbose=self.verbose)
                    enhanced_steps, status = self.tasks_solvers.plan_enhancing_solver.solve(
                        lang=self.config.lang, gen_strategy=self.config.agent_gen_stategy, query=search_plan.base_query,
                        search_steps=search_plan.search_steps,
                        steps_answers=search_plan.steps_answers[:search_step])
                    str_enhancedsteps = "\n".join(
                        [f'{i}. {gen_step}' for i, gen_step in enumerate(enhanced_steps)])
                    self.log(
                        f"RESULT: {len(enhanced_steps)}\n{str_enhancedsteps}", verbose=self.verbose)

                    if status == ReturnStatus.success:
                        enhanced_search_plan = deepcopy(search_plan)
                        enhanced_search_plan.search_steps = search_plan.search_steps[
                            :search_step] + enhanced_steps
                        enhanced_search_plan.steps_answers = search_plan.steps_answers[:search_step]

                else:
                    self.log("Улучшение шагов поиска не требуется...",
                             verbose=self.verbose)
                    enhanced_search_plan = deepcopy(search_plan)

        rinfo.status = status
        self.log(f"STATUS: {rinfo.status}", verbose=self.verbose)

        return enhanced_search_plan, rinfo
