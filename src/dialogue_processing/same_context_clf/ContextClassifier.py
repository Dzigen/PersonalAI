from copy import deepcopy
from dataclasses import dataclass, field
from .config import CTXCLS_MAIN_LOG_PATH
from ...agents.utils import AbstractAgentConnector
from typing import Tuple, Union, List, Dict, Callable, Optional
from .utils import SameCtxClsTaskSolvers, SameCtxClsAgentTasksConfig
from ...utils import ReturnInfo, Logger, AgentTaskSolver
from ...utils.cache_kv import CacheUtils
from ...utils.cache_kv.CacheOperations import CacheOperations
from ...utils.data_structs import create_id, QueryPreprocessingInfo, BaseComponentConfig, LanguageConfig
from ...db_drivers.kv_driver import KeyValueDriverConfig


@dataclass
class SameContextClfConfig(BaseComponentConfig, LanguageConfig):
    """
    :param cache_table_name: Название таблицы в структуре (базе) данных, куда будут сохраняться (кешироваться) основные результаты работы AnswersAggregator-класса. Значение по умолчанию 'same_ctx_cls_main_stage_cache'.
    :type cache_table_name: str, optional
    """
    agent_gen_stategy: Union[None, Dict[str, Union[str, int, float]]] = None
    agent_tasks_config: Union[Dict, SameCtxClsAgentTasksConfig] = field(default_factory=lambda: SameCtxClsAgentTasksConfig())

    cache_table_name: str = 'same_ctx_cls_main_stage_cache'
    log: Logger = field(default_factory=lambda: Logger(CTXCLS_MAIN_LOG_PATH))

    def to_str(self) -> str:
        return f"{self.lang}|{self.agent_gen_stategy}|{self.agent_tasks_config.to_str()}"

    @staticmethod
    def from_dict(dict_config: Dict):
        dictconfig_copy = deepcopy(dict_config)
        formated_config = SameContextClfConfig(**dictconfig_copy)
        formated_config.formate_fields()
        return formated_config

    def formate_fields(self):
        if isinstance(self.agent_tasks_config, dict):
            self.agent_tasks_config = SameCtxClsAgentTasksConfig.from_dict(self.agent_tasks_config)
        else:
            self.agent_tasks_config.formate_fields()


class SameContextClf(CacheUtils, CacheOperations):
    """
    :param cache_kvdriver_config: Конфигурация структуры данных для кеширования промежуточных результатов в рамках компонент данного класса. Значение по умолчанию None.
    :type cache_kvdriver_config: Union[KeyValueDriverConfig, None], optional
    :param cache_llm_inference: Если True, то все результаты решения атомарных LLM-задач будут кешироваться, иначе False. Значение по умолчанию True.
    :type cache_llm_inference: bool, optional
    """
    def __init__(self, agent: AbstractAgentConnector, config: Union[Dict, SameContextClfConfig] = SameContextClfConfig(),
                cache_kvdriver_config: Union[None, KeyValueDriverConfig] = None, cache_llm_inference: bool = True
                 ) -> None:
        if isinstance(config, dict):
            config: SameContextClfConfig = SameContextClfConfig.from_dict(config)
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
        self.tasks_solvers: SameCtxClsTaskSolvers = SameCtxClsTaskSolvers(
            same_ctx_solver=AgentTaskSolver(
                self.agent, self.config.agent_tasks_config.same_ctx_clf, agents_cache_config, inferencestat_config
            )
        )
        self.log = self.config.log
        self.verbose = self.config.verbose

    def get_cache_key(self, prev_user_text: str, curr_text: str) -> List[str]:
        """Формирует ключ кэша для результатов классификации сообщений.

        :return: Список строк, используемый как составной ключ кеша.
        :rtype: List[str]
        """
        str_using_agent_info = f"{self.agent.CONNECTOR_KW}:{self.agent.config.to_str()}"
        return [prev_user_text, curr_text, self.config.to_str(), str_using_agent_info]

    @CacheUtils.cache_method_output
    def perform(
        self,
        prev_user_text: str,
        curr_text: str,
    ) -> str:
        """
        """

        self.log("Выполнение разбиения сообщений пользователя на группы с помощью LLM-агента...", verbose=self.verbose)
        self.log(f"Проверяем, связано ли текущее сообщение пользователя = {curr_text} с предыдущим.\nПредыдущее = {prev_user_text}", verbose=self.verbose)

        final_answer, status = self.tasks_solvers.same_ctx_solver.solve(
            lang=self.config.lang, gen_strategy=self.config.agent_gen_stategy, curr_text=curr_text, prev_user_text=prev_user_text)

        self.log(f"Финальный ответ = {final_answer}", verbose=self.verbose)
        return final_answer
        # prompt = self._build_prompt(text, prev_context, next_context)
        # return self.llm_call(prompt)

