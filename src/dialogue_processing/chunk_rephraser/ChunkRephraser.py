from copy import deepcopy
from dataclasses import dataclass, field
from .config import RPHCHNK_MAIN_LOG_PATH
from ...agents.utils import AbstractAgentConnector
from typing import Tuple, Union, List, Dict, Callable, Optional, Any
from .utils import RephChunkTaskSolvers, RephChunkAgentTasksConfig
from ...utils import ReturnInfo, Logger, AgentTaskSolver, ReturnStatus
from ...utils.cache_kv import CacheUtils
from ...utils.cache_kv.CacheOperations import CacheOperations
from ...utils.data_structs import create_id, QueryPreprocessingInfo, BaseComponentConfig, LanguageConfig
from ...db_drivers.kv_driver import KeyValueDriverConfig


@dataclass
class RephraseChunkConfig(BaseComponentConfig, LanguageConfig):
    """
    :param cache_table_name: Название таблицы в структуре (базе) данных, куда будут сохраняться (кешироваться) основные результаты работы RephraseChunk-класса. Значение по умолчанию 'rephrase_chunk_main_stage_cache'.
    :type cache_table_name: str, optional
    """
    agent_gen_stategy: Union[None, Dict[str, Union[str, int, float]]] = None
    agent_tasks_config: Union[Dict, RephChunkAgentTasksConfig] = field(default_factory=lambda: RephChunkAgentTasksConfig())

    cache_table_name: str = 'rephrase_chunk_main_stage_cache'
    log: Logger = field(default_factory=lambda: Logger(RPHCHNK_MAIN_LOG_PATH))

    def to_str(self) -> str:
        # return f"{self.lang}|{self.agent_gen_stategy}|{self.agent_tasks_config.to_str()}"
        return f"auto|{self.agent_gen_stategy}|{self.agent_tasks_config.to_str()}"

    @staticmethod
    def from_dict(dict_config: Dict):
        dictconfig_copy = deepcopy(dict_config)
        formated_config = RephraseChunkConfig(**dictconfig_copy)
        formated_config.formate_fields()
        return formated_config

    def formate_fields(self):
        if isinstance(self.agent_tasks_config, dict):
            self.agent_tasks_config = RephChunkAgentTasksConfig.from_dict(self.agent_tasks_config)
        else:
            self.agent_tasks_config.formate_fields()


class RephraseChunk(CacheUtils, CacheOperations):
    """
    :param cache_kvdriver_config: Конфигурация структуры данных для кеширования промежуточных результатов в рамках компонент данного класса. Значение по умолчанию None.
    :type cache_kvdriver_config: Union[KeyValueDriverConfig, None], optional
    :param cache_llm_inference: Если True, то все результаты решения атомарных LLM-задач будут кешироваться, иначе False. Значение по умолчанию True.
    :type cache_llm_inference: bool, optional
    """
    def __init__(self, agent: AbstractAgentConnector, config: Union[Dict, RephraseChunkConfig] = RephraseChunkConfig(),
                cache_kvdriver_config: Union[None, KeyValueDriverConfig] = None, cache_llm_inference: bool = True
                 ) -> None:
        if isinstance(config, dict):
            config: RephraseChunkConfig = RephraseChunkConfig.from_dict(config)
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
        self.tasks_solvers: RephChunkTaskSolvers = RephChunkTaskSolvers(
            reph_chunk_solver=AgentTaskSolver(
                self.agent, self.config.agent_tasks_config.reph_chunk, agents_cache_config, inferencestat_config
            ),
            reject_answer_cls_solver=AgentTaskSolver(
                self.agent, self.config.agent_tasks_config.reject_answer_cls, agents_cache_config, inferencestat_config
            )
        )
        self.log = self.config.log
        self.verbose = self.config.verbose

    def get_cache_key(self, chunk_messages: List[Dict[str, Any]]) -> List[str]:
        """Формирует ключ кэша для результатов классификации сообщений.

        :return: Список строк, используемый как составной ключ кеша.
        :rtype: List[str]
        """
        msgs_text = []
        for msg in chunk_messages:
            msg_text = msg.get("processed_text") or msg.get("text") or ""
            msgs_text.append(msg_text)
        str_messages = ';'.join(msgs_text)
        str_using_agent_info = f"{self.agent.CONNECTOR_KW}:{self.agent.config.to_str()}"
        return [str_messages, self.config.to_str(), str_using_agent_info]

    @CacheUtils.cache_method_output
    def perform(
        self,
        chunk_messages: List[Dict[str, Any]]
    ) -> List[str]:
        """
        """

        self.log("Выполнение перефразирования сообщений с помощью LLM-агента...", verbose=self.verbose)

        final_answer, status = self.tasks_solvers.reph_chunk_solver.solve(
            lang=self.config.lang, gen_strategy=self.config.agent_gen_stategy, chunk_messages=chunk_messages)

        parsed_responce, raw_responce = final_answer
        self.log(f"Cырой ответ = {raw_responce}", verbose=self.verbose)
        self.log(f"Распаршенный ответ = {parsed_responce}", verbose=self.verbose)

        is_reject_answer = False
        if status == ReturnStatus.success:
            self.log(f"Проверяем, что мы получили валидный ответ", verbose=self.verbose)
            is_reject_answer, status = self.tasks_solvers.reject_answer_cls_solver.solve(
                    lang=self.config.lang, gen_strategy=self.config.agent_gen_stategy, answer=raw_responce)

            self.log(f"Got reject answer = {is_reject_answer}", verbose=self.verbose)

        return parsed_responce, raw_responce, is_reject_answer



        # self.log(f"Финальный ответ = {final_answer}", verbose=self.verbose)
        # return final_answer
