from copy import deepcopy
from dataclasses import dataclass, field
from .config import ASUCLS_MAIN_LOG_PATH
from ...agents.utils import AbstractAgentConnector
from typing import Tuple, Union, List, Dict, Callable, Optional
from .utils import AssistUseClsTaskSolvers, AssistUseClsAgentTasksConfig
from ...utils import ReturnInfo, Logger, AgentTaskSolver
from ...utils.cache_kv import CacheUtils
from ...utils.cache_kv.CacheOperations import CacheOperations
from ...utils.data_structs import create_id, QueryPreprocessingInfo, BaseComponentConfig, LanguageConfig
from ...db_drivers.kv_driver import KeyValueDriverConfig


@dataclass
class AssistUsefulClfConfig(BaseComponentConfig, LanguageConfig):
    """
    :param cache_table_name: Название таблицы в структуре (базе) данных, куда будут сохраняться (кешироваться) основные результаты работы AnswersAggregator-класса. Значение по умолчанию 'assist_use_cls_main_stage_cache'.
    :type cache_table_name: str, optional
    """
    agent_gen_stategy: Union[None, Dict[str, Union[str, int, float]]] = None
    agent_tasks_config: Union[Dict, AssistUseClsAgentTasksConfig] = field(default_factory=lambda: AssistUseClsAgentTasksConfig())

    cache_table_name: str = 'assist_use_cls_main_stage_cache'
    log: Logger = field(default_factory=lambda: Logger(ASUCLS_MAIN_LOG_PATH))

    def to_str(self) -> str:
        return f"{self.lang}|{self.agent_gen_stategy}|{self.agent_tasks_config.to_str()}"

    @staticmethod
    def from_dict(dict_config: Dict):
        dictconfig_copy = deepcopy(dict_config)
        formated_config = AssistUsefulClfConfig(**dictconfig_copy)
        formated_config.formate_fields()
        return formated_config

    def formate_fields(self):
        if isinstance(self.agent_tasks_config, dict):
            self.agent_tasks_config = AssistUseClsAgentTasksConfig.from_dict(self.agent_tasks_config)
        else:
            self.agent_tasks_config.formate_fields()


class AssistUsefulClf(CacheUtils, CacheOperations):
    """
    :param cache_kvdriver_config: Конфигурация структуры данных для кеширования промежуточных результатов в рамках компонент данного класса. Значение по умолчанию None.
    :type cache_kvdriver_config: Union[KeyValueDriverConfig, None], optional
    :param cache_llm_inference: Если True, то все результаты решения атомарных LLM-задач будут кешироваться, иначе False. Значение по умолчанию True.
    :type cache_llm_inference: bool, optional
    """
    def __init__(self, agent: AbstractAgentConnector, config: Union[Dict, AssistUsefulClfConfig] = AssistUsefulClfConfig(),
                cache_kvdriver_config: Union[None, KeyValueDriverConfig] = None, cache_llm_inference: bool = True
                 ) -> None:
        if isinstance(config, dict):
            config: AssistUsefulClfConfig = AssistUsefulClfConfig.from_dict(config)
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
        self.tasks_solvers: AssistUseClsTaskSolvers = AssistUseClsTaskSolvers(
            assist_use_solver=AgentTaskSolver(
                self.agent, self.config.agent_tasks_config.assist_use_clf, agents_cache_config, inferencestat_config
            )
        )
        self.log = self.config.log
        self.verbose = self.config.verbose

    def get_cache_key(self, assistant_text: str, prev_user_text: str, next_user_text: str) -> List[str]:
        """Формирует ключ кэша для результатов классификации сообщений.

        :return: Список строк, используемый как составной ключ кеша.
        :rtype: List[str]
        """
        str_using_agent_info = f"{self.agent.CONNECTOR_KW}:{self.agent.config.to_str()}"
        return [assistant_text, prev_user_text, next_user_text, self.config.to_str(), str_using_agent_info]

    @CacheUtils.cache_method_output
    def perform(
        self,
        assistant_text: str,
        prev_user_text: str,
        next_user_text: str
    ) -> str:
        """
        """

        self.log("Выполнение фильтрации сообщений ассистента с помощью LLM-агента...", verbose=self.verbose)
        self.log(f"Проверяем, необходимо ли текущее сообщения ассистента = {assistant_text} для более точного извлечения информации и пользователе.\nПредыдущее сообщения пользователя = {prev_user_text}.\n Следующее сообщение пользователя = {next_user_text}", verbose=self.verbose)

        final_answer, status = self.tasks_solvers.assist_use_solver.solve(
            lang=self.config.lang, gen_strategy=self.config.agent_gen_stategy, assistant_text=assistant_text, prev_user_text=prev_user_text, next_user_text=next_user_text)

        self.log(f"Финальный ответ = {final_answer}", verbose=self.verbose)
        return final_answer
