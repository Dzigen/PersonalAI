from copy import deepcopy
from dataclasses import dataclass, field
from .config import QSTRPH_MAIN_LOG_PATH
from ...agents.utils import AbstractAgentConnector
from typing import Tuple, Union, List, Dict, Callable, Optional, Any
from .utils import QuestRephTaskSolvers, QuestRephAgentTasksConfig
from ...utils import ReturnInfo, Logger, AgentTaskSolver, ReturnStatus
from ...utils.cache_kv import CacheUtils
from ...utils.cache_kv.CacheOperations import CacheOperations
from ...utils.data_structs import create_id, BaseComponentConfig, LanguageConfig
from ...db_drivers.kv_driver import KeyValueDriverConfig


@dataclass
class QuestRephraserConfig(BaseComponentConfig, LanguageConfig):
    """
    :param cache_table_name: Название таблицы в структуре (базе) данных, куда будут сохраняться (кешироваться) основные результаты работы QuestRephraser-класса. Значение по умолчанию 'quest_rephrase_main_stage_cache'.
    :type cache_table_name: str, optional
    """
    agent_gen_stategy: Union[None, Dict[str, Union[str, int, float]]] = None
    agent_tasks_config: Union[Dict, QuestRephAgentTasksConfig] = field(default_factory=lambda: QuestRephAgentTasksConfig())

    cache_table_name: str = 'quest_rephrase_main_stage_cache'
    log: Logger = field(default_factory=lambda: Logger(QSTRPH_MAIN_LOG_PATH))

    def to_str(self) -> str:
        return f"{self.lang}|{self.agent_gen_stategy}|{self.agent_tasks_config.to_str()}"

    @staticmethod
    def from_dict(dict_config: Dict):
        dictconfig_copy = deepcopy(dict_config)
        formated_config = QuestRephraserConfig(**dictconfig_copy)
        formated_config.formate_fields()
        return formated_config

    def formate_fields(self):
        if isinstance(self.agent_tasks_config, dict):
            self.agent_tasks_config = QuestRephAgentTasksConfig.from_dict(self.agent_tasks_config)
        else:
            self.agent_tasks_config.formate_fields()


class QuestRephraser(CacheUtils, CacheOperations):
    """
    :param cache_kvdriver_config: Конфигурация структуры данных для кеширования промежуточных результатов в рамках компонент данного класса. Значение по умолчанию None.
    :type cache_kvdriver_config: Union[KeyValueDriverConfig, None], optional
    :param cache_llm_inference: Если True, то все результаты решения атомарных LLM-задач будут кешироваться, иначе False. Значение по умолчанию True.
    :type cache_llm_inference: bool, optional
    """
    def __init__(self, agent: AbstractAgentConnector, config: Union[Dict, QuestRephraserConfig] = QuestRephraserConfig(),
                cache_kvdriver_config: Union[None, KeyValueDriverConfig] = None, cache_llm_inference: bool = True
                 ) -> None:
        if isinstance(config, dict):
            config: QuestRephraserConfig = QuestRephraserConfig.from_dict(config)
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
        inferencestat_config = None
        self.tasks_solvers: QuestRephTaskSolvers = QuestRephTaskSolvers(
            quest_rephraser_solver=AgentTaskSolver(
                self.agent, self.config.agent_tasks_config.quest_rephraser, agents_cache_config, inferencestat_config
            ),
            reject_answer_cls_solver=AgentTaskSolver(
                self.agent, self.config.agent_tasks_config.reject_answer_cls, agents_cache_config, inferencestat_config
            )
        )
        self.log = self.config.log
        self.verbose = self.config.verbose

    def get_cache_key(self, question: str) -> List[str]:
        """Формирует ключ кэша для результатов переформулированя вопросов.

        :return: Список строк, используемый как составной ключ кеша.
        :rtype: List[str]
        """
        str_using_agent_info = f"{self.agent.CONNECTOR_KW}:{self.agent.config.to_str()}"
        return [question, self.config.to_str(), str_using_agent_info]

    @CacheUtils.cache_method_output
    def perform(
        self,
        question: str
    ) -> List[str]:

        self.log("Выполнение перефразирования вопроса с помощью LLM-агента...", verbose=self.verbose)

        final_answer, status = self.tasks_solvers.quest_rephraser_solver.solve(
            lang=self.config.lang, gen_strategy=self.config.agent_gen_stategy, question=question)

        is_reject_answer = False
        if status == ReturnStatus.success:
            self.log(f"Проверяем, что мы получили валидный ответ", verbose=self.verbose)
            is_reject_answer, status = self.tasks_solvers.reject_answer_cls_solver.solve(
                    lang=self.config.lang, gen_strategy=self.config.agent_gen_stategy, answer=final_answer)

            self.log(f"Got reject answer = {is_reject_answer}", verbose=self.verbose)


        self.log(f"Финальный ответ = {final_answer}", verbose=self.verbose)
        return final_answer, is_reject_answer
