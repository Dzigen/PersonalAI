from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from .config import FACT_PRESERVE_MAIN_LOG_PATH
from ...agents.utils import AbstractAgentConnector
from typing import Tuple, Union, List, Dict, Callable, Optional
from .utils import FactPreserverTaskSolvers, FactPreserverAgentTasksConfig
from ...utils.cache_kv import CacheUtils
from ...utils.cache_kv.CacheOperations import CacheOperations
from ...utils import ReturnInfo, Logger, AgentTaskSolver, ReturnStatus
from ...utils.data_structs import create_id, QueryPreprocessingInfo, BaseComponentConfig, LanguageConfig
from ...db_drivers.kv_driver import KeyValueDriverConfig

SummarizeLLMCallable = Callable[[str], str]



@dataclass
class FactPreserverConfig(BaseComponentConfig, LanguageConfig):
    """Конфигурация компоненты суммаризации сообщений.

    :param max_chunk_tokens: Лимит токенов для одного сообщения. Если длина сообщения
        превышает данный лимит, то перед дальнейшей обработкой будет выполнена
        факт-сохраняющая суммаризация этого сообщения.
    :type max_chunk_tokens: int
    :param neighbor_max_tokens: Максимальное количество токенов, которые можно
        использовать из соседних сообщений (до и после) для формирования краткого
        контекста при факт-сохраняющей суммаризации.
    :type neighbor_max_tokens: int
    :param cache_table_name: Название таблицы в структуре (базе) данных, куда будут сохраняться (кешироваться) основные результаты работы AnswersAggregator-класса. Значение по умолчанию 'fact_preserving_main_stage_cache'.
    :type cache_table_name: str, optional
    """
    agent_gen_stategy: Union[None, Dict[str, Union[str, int, float]]] = None
    agent_tasks_config: Union[Dict, FactPreserverAgentTasksConfig] = field(default_factory=lambda: FactPreserverAgentTasksConfig())

    max_chunk_tokens: int = 2000
    neighbor_max_tokens: int = 200

    cache_table_name: str = 'fact_preserving_main_stage_cache'
    log: Logger = field(default_factory=lambda: Logger(FACT_PRESERVE_MAIN_LOG_PATH))

    def to_str(self) -> str:
        return f"{self.lang}|{self.agent_gen_stategy}|{self.agent_tasks_config.to_str()}"

    @staticmethod
    def from_dict(dict_config: Dict):
        dictconfig_copy = deepcopy(dict_config)
        formated_config = FactPreserverConfig(**dictconfig_copy)
        formated_config.formate_fields()
        return formated_config

    def formate_fields(self):
        if isinstance(self.agent_tasks_config, dict):
            self.agent_tasks_config = FactPreserverAgentTasksConfig.from_dict(self.agent_tasks_config)
        else:
            self.agent_tasks_config.formate_fields()


class FactPreserv(CacheUtils, CacheOperations):
    """Компонента для факт-сохраняющей суммаризации сообщений диалога.

    Данный класс инкапсулирует логику формирования промпта для LLM и
    вызова внешнего инструмента суммаризации. Непосредственная обвязка
    с LLM (через агентные задачи или другой интерфейс) передаётся в виде
    функции-колбэка ``llm_call``.

    :param llm_call: Функция-обёртка над LLM, принимающая на вход подготовленный
        текстовый промпт и возвращающая ответ модели в виде строки.
    :type llm_call: Callable[[str], str]
    :param cache_kvdriver_config: Конфигурация структуры данных для кеширования промежуточных результатов в рамках компонент данного класса. Значение по умолчанию None.
    :type cache_kvdriver_config: Union[KeyValueDriverConfig, None], optional
    :param cache_llm_inference: Если True, то все результаты решения атомарных LLM-задач будут кешироваться, иначе False. Значение по умолчанию True.
    :type cache_llm_inference: bool, optional
    """
    def __init__(self, agent: AbstractAgentConnector, config: Union[Dict, FactPreserverConfig] = FactPreserverConfig(),
                cache_kvdriver_config: Union[None, KeyValueDriverConfig] = None, cache_llm_inference: bool = True
                 ) -> None:
        if isinstance(config, dict):
            config: FactPreserverConfig = FactPreserverConfig.from_dict(config)
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
        self.tasks_solvers: FactPreserverTaskSolvers = FactPreserverTaskSolvers(
            fact_preserving_solver=AgentTaskSolver(
                self.agent, self.config.agent_tasks_config.msg_summarisation, agents_cache_config, inferencestat_config
            ),
            reject_answer_cls_solver=AgentTaskSolver(
                self.agent, self.config.agent_tasks_config.reject_answer_cls, agents_cache_config, inferencestat_config
            )
        )
        self.log = self.config.log
        self.verbose = self.config.verbose


    def get_cache_key(self, text: str, prev_context: str, next_context: str) -> List[str]:
        """Формирует ключ кэша для результатов суммаризации сообщений.

        :return: Список строк, используемый как составной ключ кеша.
        :rtype: List[str]
        """
        str_using_agent_info = f"{self.agent.CONNECTOR_KW}:{self.agent.config.to_str()}"
        return [text, prev_context, next_context, self.config.to_str(), str_using_agent_info]

    @CacheUtils.cache_method_output
    def perform(
        self,
        text: str,
        prev_context: Optional[str] = None,
        next_context: Optional[str] = None,
    ) -> str:
        """Выполняет факт-сохраняющую суммаризацию одного сообщения.

        Формирует промпт, в котором исходное сообщение дополняется
        кратким контекстом до и после него (при наличии), и передаёт
        этот промпт во внешнюю LLM через переданную функцию ``llm_call``.

        Важно, что суммаризация должна сохранять все факты, сущности и
        связи, содержащиеся в исходном сообщении. Допускается только
        сжатие формулировок и устранение повторов, но не потеря знаний.

        :param text: Исходный текст сообщения, подлежащего суммаризации.
        :type text: str
        :param prev_context: Краткий контекст из предыдущего сообщения
            (если он есть), уже обрезанный по числу токенов.
        :type prev_context: Optional[str]
        :param next_context: Краткий контекст из следующего сообщения
            (если он есть), уже обрезанный по числу токенов.
        :type next_context: Optional[str]
        :return: Суммаризованный текст сообщения с сохранением фактов и связей.
        :rtype: str
        """

        self.log("Выполнение суммаризации ответов с помощью LLM-агента...", verbose=self.verbose)

        self.log(f"Текст для суммаризации = {text[:100]}", verbose=self.verbose)
        final_answer, status = self.tasks_solvers.fact_preserving_solver.solve(
            lang=self.config.lang, gen_strategy=self.config.agent_gen_stategy, text=text, prev_context=prev_context, next_context=next_context)

        if status == ReturnStatus.success:
            self.log(f"Проверяем, что мы получили валидный ответ", verbose=self.verbose)
            is_reject_answer, status = self.tasks_solvers.reject_answer_cls_solver.solve(
                    lang=self.config.lang, gen_strategy=self.config.agent_gen_stategy, answer=final_answer)

            self.log(f"Got reject answer = {is_reject_answer}", verbose=self.verbose)

            if is_reject_answer:
                final_answer = text

        self.log(f"Финальный ответ = {final_answer}", verbose=self.verbose)
        return final_answer
        # prompt = self._build_prompt(text, prev_context, next_context)
        # return self.llm_call(prompt)

