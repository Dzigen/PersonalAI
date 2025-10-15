from dataclasses import dataclass, field
from typing import Tuple, Union, List, Dict
from copy import deepcopy

from .config import PLANENH_MAIN_LOG_PATH, DEFAULT_PLANINIT_TASK_CONFIG, \
    DEFAULT_PLANENH_TASK_CONFIG, DEFAUL_ENHCLASSIFY_TASK_CONFIG
from ..utils import SearchPlanInfo
from ......utils import ReturnInfo, Logger, AgentTaskSolverConfig, AgentTaskSolver
from ......utils.errors import ReturnStatus
from ......agents.utils import AbstractAgentConnector
from ......utils.data_structs import create_id
from ......db_drivers.kv_driver import KeyValueDriverConfig
from ......utils.cache_kv import CacheUtils
from ......utils.agent_stat_analyzer import AgentStatAnalyzerConfig


@dataclass
class SearchPlanEnhancerConfig:
    """Конфигурация SearchPlanEnhancer-стадии MediumQA-ризонера.

    :param lang: Язык, который будет использоваться в подаваемом на вход тексте. На основании выбранного языка будут использоваться соответствующие промпты при инференсе LLM-агента. Если 'auto', то язык определяется автоматически. Значение по умолчанию 'auto'.
    :type lang: str, optional
    :param agent_gen_stategy: Стратегия генерации текста для используемого LLM-агента. В случае None-значение будет использоваться стратегия по умолчанию. Значение по умолчанию None.
    :type agent_gen_stategy: Union[None,Dict[str, Union[str, int, float]]], optional
    :param plan_initing_agent_task_config: Конфигурация атомарной задачи для LLM-агента по генерации базового/стартового плана поиска. Значение по умолчанию DEFAULT_PLANINIT_TASK_CONFIG.
    :type plan_initing_agent_task_config: AgentTaskSolverConfig, optional
    :param enhance_classifier_agent_task_config: Конфигурация атомарной задачи для LLM-агента по определению необходимости (бинарная классификация) модификации существующего плана поиска. Значение по умолчанию DEFAUL_ENHCLASSIFY_TASK_CONFIG.
    :type enhance_classifier_agent_task_config: AgentTaskSolverConfig, optional
    :param plan_enhancing_agent_task_config: Конфигурация атомарной задачи для LLM-агента по подификации/перегенерации не пройденных шагов поиска в рамках существующего плана. Значение по умолчанию DEFAULT_PLANENH_TASK_CONFIG.
    :type plan_enhancing_agent_task_config: AgentTaskSolverConfig, optional
    :param cache_table_name: Название таблицы в структуре (базе) данных, куда будут сохраняться (кешироваться) основные результаты работы SearchPlanEnhancer-класса. Значение по умолчанию 'medreasn_planenh_main_stage_cache'.
    :type cache_table_name: str, optional
    :param log: Отладочный класс для журналирования/мониторинга поведения инициализируемой комопненты. Значение по умолчанию Logger(PLANENH_MAIN_LOG_PATH).
    :type log: Logger, optional
    :param verbose: Если True, то информация о поведении класса будет сохраняться в stdout и файл-журналирования (log), иначе только в файл. Значение по умолчанию False.
    :type verbose: bool, optional
    """
    lang: str = 'auto'
    agent_gen_stategy: Union[None, Dict[str, Union[str, int, float]]] = None
    plan_initing_agent_task_config: AgentTaskSolverConfig = field(
        default_factory=lambda: DEFAULT_PLANINIT_TASK_CONFIG)
    enhance_classifier_agent_task_config: AgentTaskSolverConfig = field(
        default_factory=lambda: DEFAUL_ENHCLASSIFY_TASK_CONFIG)
    plan_enhancing_agent_task_config: AgentTaskSolverConfig = field(
        default_factory=lambda: DEFAULT_PLANENH_TASK_CONFIG)

    cache_table_name: str = 'medreasn_planenh_main_stage_cache'
    log: Logger = field(default_factory=lambda: Logger(PLANENH_MAIN_LOG_PATH))
    verbose: bool = False

    def to_str(self):
        str_pi_config = self.plan_initing_agent_task_config.version
        str_ec_config = self.enhance_classifier_agent_task_config.version
        str_pe_config = self.plan_enhancing_agent_task_config.version
        return f"{self.lang}|{self.agent_gen_stategy}|{str_pi_config}|{str_ec_config}|{str_pe_config}"


class SearchPlanEnhancer(CacheUtils):
    """Верхнеуровневый класс стадии #1 medium QA-конвейера для выполнения генерации/модификации плана поиска/извлечения информации из графа знаний.

    :param agent: Коннектор к конкретному LLM-агенту для выполнения inference-операций.
    :type agent: AbstractAgentConnector
    :param config: Конфигурация SearchPlanEnhancer-стадии. Значение по умолчанию SearchPlanEnhancerConfig().
    :type config: SearchPlanEnhancerConfig, optional
    :param cache_kvdriver_config: Конфигурация структуры данных для кеширования промежуточных результатов в рамках компонент данного класса. Значение по умолчению None.
    :type cache_kvdriver_config: Union[KeyValueDriverConfig, None], optional
    :param cache_llm_inference: Если True, то все результаты решения атомарных LLM-задач будут кешироваться, иначе False. Значение по умолчанию True.
    :type cache_llm_inference: bool, optional
    :param inferencestat_config: Конфигурация компоненты для сбора информации и расчёта статистик по результатам выполнения inference-операциий в рамках LLM-задач. Значение по умолчанию None.
    :type inferencestat_config: Union[None, AgentStatAnalyzerConfig], optional
    """

    def __init__(self, agent: AbstractAgentConnector, config: SearchPlanEnhancerConfig = SearchPlanEnhancerConfig(),
                 cache_kvdriver_config: Union[None, KeyValueDriverConfig] = None, cache_llm_inference: bool = True,
                 inferencestat_config: Union[None, AgentStatAnalyzerConfig] = None):
        self.config = config

        self.cachekv = self.init_cachekv(
            cache_kvdriver_config, config.cache_table_name)

        self.agent = agent
        agents_cache_config = None
        if cache_llm_inference:
            agents_cache_config = cache_kvdriver_config

        self.tasks_solvers: Dict[str, AgentTaskSolver] = dict()
        self.tasks_solvers['plan_initialing_solver'] = AgentTaskSolver(
            self.agent, self.config.plan_initing_agent_task_config,
            agents_cache_config, inferencestat_config)
        self.tasks_solvers['enhance_classify_solver'] = AgentTaskSolver(
            self.agent, self.config.enhance_classifier_agent_task_config,
            agents_cache_config, inferencestat_config)
        self.tasks_solvers['plan_enhancing_solver'] = AgentTaskSolver(
            self.agent, self.config.plan_enhancing_agent_task_config,
            agents_cache_config, inferencestat_config)

        self.log = self.config.log
        self.verbose = self.config.verbose

    def get_agent_tgen_stat(self) -> Union[None, Dict[str, Union[None, Dict]]]:
        return {name: solver.get_agent_tgen_stat() for name, solver in self.tasks_solvers.items()}

    def get_cache_stat(self) -> Dict[str, Union[None, Dict]]:
        cache_stat = {'SearchPlanEnhancer': None if self.cachekv is None else self.cachekv.kv_conn.count_items()}
        tasks_caches = {name: solver.get_cache_stat() for name, solver in self.tasks_solvers.items()}
        cache_stat.update(tasks_caches)
        return cache_stat

    def clear_kv_caches(self, level: str = 'all') -> None:
        if not isinstance(level, str):
            raise TypeError(
                f"Аргумент переменной 'level' должен иметь тип 'str'; сейчас аргумент имеет тип '{type(level)}'")
        if level not in ['all', 'current', 'other']:
            raise ValueError(
                f"Аргумент переменной 'level' должен принимать одно из трёх значенией: 'all', 'current' или 'other'. Полученное значение: '{level}'")

        if level in ['current', 'all']:
            self.cachekv.clear()

        if level in ['other', 'all']:
            self.tasks_solvers['plan_initialing_solver'].cachekv.clear()
            self.tasks_solvers['enhance_classify_solver'].cachekv.clear()
            self.tasks_solvers['plan_enhancing_solver'].cachekv.clear()

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
        self.log("START SEARCH-PLAN INITING/ENHANCING...",
                 verbose=self.config.verbose)
        self.log(
            f"QUERY ID: {create_id(search_plan.base_query)}", verbose=self.config.verbose)
        self.log(f"CURRENT PLAN: {search_plan}", verbose=self.config.verbose)
        enhanced_search_plan, rinfo = None, ReturnInfo()

        if search_step < 0:
            raise ValueError

        if search_step == 0:
            self.log("Генерируем план поиска с нуля...", verbose=self.verbose)
            new_search_steps, status = self.tasks_solvers['plan_initialing_solver'].solve(
                lang=self.config.lang, gen_strategy=self.config.agent_gen_stategy, query=search_plan.base_query)
            str_searchplan = "\n".join(
                [f'{i}. {gen_step}' for i, gen_step in enumerate(new_search_steps)])
            self.log(
                f"RESULT: {len(new_search_steps)}\n{str_searchplan}", verbose=self.config.verbose)

            if status == ReturnStatus.success:
                enhanced_search_plan = deepcopy(search_plan)
                enhanced_search_plan.search_steps = new_search_steps
                enhanced_search_plan.steps_answers = []
        else:
            self.log(
                "Выполняем проверку на необходимость улучшения следующих шагов поиска в плане...", verbose=self.verbose)
            need_enhance, status = self.tasks_solvers['enhance_classify_solver'].solve(
                lang=self.config.lang, gen_strategy=self.config.agent_gen_stategy, query=search_plan.base_query,
                search_steps=search_plan.search_steps, steps_answers=search_plan.steps_answers[:search_step])
            self.log(f"RESULT: {need_enhance}", verbose=self.config.verbose)

            if status == ReturnStatus.success:
                if need_enhance:
                    self.log("Улучшаем следующие шаги поиска в плане...",
                             verbose=self.verbose)
                    enhanced_steps, status = self.tasks_solvers['plan_enhancing_solver'].solve(
                        lang=self.config.lang, gen_strategy=self.config.agent_gen_stategy, query=search_plan.base_query,
                        search_steps=search_plan.search_steps,
                        steps_answers=search_plan.steps_answers[:search_step])
                    str_enhancedsteps = "\n".join(
                        [f'{i}. {gen_step}' for i, gen_step in enumerate(enhanced_steps)])
                    self.log(
                        f"RESULT: {len(enhanced_steps)}\n{str_enhancedsteps}", verbose=self.config.verbose)

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
        self.log(f"STATUS: {rinfo.status}", verbose=self.config.verbose)

        return enhanced_search_plan, rinfo
