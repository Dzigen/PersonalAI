from copy import deepcopy
from dataclasses import dataclass, field
from .config import ANSWRPH_MAIN_LOG_PATH
from ...agents.utils import AbstractAgentConnector
from typing import Tuple, Union, List, Dict, Callable, Optional, Any
from .utils import AnswRephTaskSolvers, AnswRephAgentTasksConfig
from ...utils import ReturnInfo, Logger, AgentTaskSolver, ReturnStatus
from ...utils.cache_kv import CacheUtils
from ...utils.cache_kv.CacheOperations import CacheOperations
from ...utils.data_structs import create_id, BaseComponentConfig, LanguageConfig
from ...db_drivers.kv_driver import KeyValueDriverConfig


@dataclass
class AnswerRephraserConfig(BaseComponentConfig, LanguageConfig):
    """
    :param cache_table_name: Название таблицы в структуре (базе) данных, куда будут сохраняться (кешироваться) основные результаты работы AnswerRephraser-класса. Значение по умолчанию 'answ_rephrase_main_stage_cache'.
    :type cache_table_name: str, optional
    """
    agent_gen_stategy: Union[None, Dict[str, Union[str, int, float]]] = None
    agent_tasks_config: Union[Dict, AnswRephAgentTasksConfig] = field(default_factory=lambda: AnswRephAgentTasksConfig())

    cache_table_name: str = 'answ_rephrase_main_stage_cache'
    log: Logger = field(default_factory=lambda: Logger(ANSWRPH_MAIN_LOG_PATH))

    def to_str(self) -> str:
        return f"{self.lang}|{self.agent_gen_stategy}|{self.agent_tasks_config.to_str()}"

    @staticmethod
    def from_dict(dict_config: Dict):
        dictconfig_copy = deepcopy(dict_config)
        formated_config = AnswerRephraserConfig(**dictconfig_copy)
        formated_config.formate_fields()
        return formated_config

    def formate_fields(self):
        if isinstance(self.agent_tasks_config, dict):
            self.agent_tasks_config = AnswRephAgentTasksConfig.from_dict(self.agent_tasks_config)
        else:
            self.agent_tasks_config.formate_fields()


class AnswerRephraser(CacheUtils, CacheOperations):
    """
    :param cache_kvdriver_config: Конфигурация структуры данных для кеширования промежуточных результатов в рамках компонент данного класса. Значение по умолчанию None.
    :type cache_kvdriver_config: Union[KeyValueDriverConfig, None], optional
    :param cache_llm_inference: Если True, то все результаты решения атомарных LLM-задач будут кешироваться, иначе False. Значение по умолчанию True.
    :type cache_llm_inference: bool, optional
    """
    def __init__(self, agent: AbstractAgentConnector, config: Union[Dict, AnswerRephraserConfig] = AnswerRephraserConfig(),
                cache_kvdriver_config: Union[None, KeyValueDriverConfig] = None, cache_llm_inference: bool = True
                 ) -> None:
        if isinstance(config, dict):
            config: AnswerRephraserConfig = AnswerRephraserConfig.from_dict(config)
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
        self.tasks_solvers: AnswRephTaskSolvers = AnswRephTaskSolvers(
            answer_rephraser_solver=AgentTaskSolver(
                self.agent, self.config.agent_tasks_config.answer_rephraser, agents_cache_config, inferencestat_config
            )
        )
        self.log = self.config.log
        self.verbose = self.config.verbose

    def get_cache_key(self, question: str, rephrased_question: str, raw_answer: str) -> List[str]:
        """Формирует ключ кэша для результатов переформулированя вопросов.

        :return: Список строк, используемый как составной ключ кеша.
        :rtype: List[str]
        """
        str_using_agent_info = f"{self.agent.CONNECTOR_KW}:{self.agent.config.to_str()}"
        return [question, rephrased_question, raw_answer, self.config.to_str(), str_using_agent_info]

    @CacheUtils.cache_method_output
    def perform(
        self,
        question: str,
        rephrased_question: str,
        raw_answer: str
    ) -> List[str]:

        self.log("Выполнение перефразирования ответа с помощью LLM-агента...", verbose=self.verbose)

        final_answer, status = self.tasks_solvers.answer_rephraser_solver.solve(
            lang=self.config.lang, gen_strategy=self.config.agent_gen_stategy, question=question, rephrased_question=rephrased_question, raw_answer=raw_answer)

        self.log(f"Финальный ответ = {final_answer}", verbose=self.verbose)
        return final_answer
