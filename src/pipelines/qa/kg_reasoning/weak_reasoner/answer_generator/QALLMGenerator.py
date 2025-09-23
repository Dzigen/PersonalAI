from typing import List, Tuple, Union, Dict
from dataclasses import dataclass, field
from copy import deepcopy
import hashlib

from .configs import DEFAULT_AG_TASK_CONFIG, AG_MAIN_LOG_PATH
from ......utils.data_structs import Triplet, RelationType, create_id, TripletCreator
from ......utils.errors import STATUS_MESSAGE
from ......agents.utils import AbstractAgentConnector
from ......utils import Logger, ReturnInfo, ReturnStatus, AgentTaskSolverConfig, AgentTaskSolver
from ......utils.cache_kv import CacheUtils
from ......db_drivers.kv_driver import KeyValueDriverConfig


@dataclass
class QALLMGeneratorConfig:
    """Конфигурация "Question Answering"-стадии QA-конвейера.

    :param lang: Язык, который будет использоваться в подаваемом на вход тексте. На основании выбранного языка будут использоваться соответствующие промпты для инференса LLM-агента. Если 'auto', то язык определяется автоматически. Значение по умолчанию 'auto'.
    :type lang: str, optional
    :param agent_gen_stategy: Стратегия генерации текста для используемого LLM-агента. В случае None-значение будет использоваться стратегия по умолчанию. Значение по умолчанию None.
    :type agent_gen_stategy: Union[None,Dict[str, Union[str, int, float]]], optional
    :param ag_task_config: Конфигурация атомарной задачи для LLM-агента по условной генерации ответа на вопрос. Значение по умолчанию DEFAULT_AG_TASK_CONFIG.
    :type ag_task_config: AgentTaskSolverConfig, optional
    :param relation_type: Типы триплетов, которые могут присутствовать в контексте для генерации ответа на user-вопрос. Значение по умолчанию [RelationType.simple, RelationType.hyper, RelationType.episodic].
    :type relation_type: List[RelationType], optional
    :param cache_table_name: Название таблицы в структуре (базе) данных, куда будут сохраняться (кешироваться) основные результаты работы QALLMGenerator-класса. Значение по умолчанию 'qa_agenerator_stage_cache'.
    :type cache_table_name: str, optional
    :param log: Отладочный класс для журналирования/мониторинга поведения инициализируемой компоненты. Значение по умолчанию Logger(AG_MAIN_LOG_PATH).
    :type log: Logger, optional
    :param verbose: Если True, то информация о поведении класса будет сохраняться в stdout и файл-журналирования (log), иначе только в файл. Значение по умолчанию False.
    :type verbose: bool, optional
    """
    lang: str = "auto"
    agent_gen_stategy: Union[None, Dict[str, Union[str, int, float]]] = None
    ag_task_config: AgentTaskSolverConfig = field(
        default_factory=lambda: DEFAULT_AG_TASK_CONFIG)

    relation_type: List[RelationType] = field(default_factory=lambda: [
                                              RelationType.simple, RelationType.hyper, RelationType.episodic])

    cache_table_name: Union[str, None] = 'qa_agenerator_stage_cache'
    log: Logger = field(default_factory=lambda: Logger(AG_MAIN_LOG_PATH))
    verbose: bool = False

    def to_str(self):
        str_relations = ";".join(
            list(map(lambda v: v.value, self.relation_type)))
        return f"{self.lang}|{self.agent_gen_stategy}|{self.ag_task_config.version}|{str_relations}"


class QALLMGenerator(CacheUtils):
    """Верхнеуровневый класс четвёртой стадии QA-конвейера для генерации ответа на user-вопрос,
    обусловленного извлечённой информацией из памяти (графа знаний) ассистента.

    :param agent: Коннектор к конкретному LLM-агенту для выполнения inference-операций.
    :type agent: AbstractAgentConnector
    :param config: Конфигурация "Answer-generation"-стадии. Значение по умолчанию QALLMGeneratorConfig().
    :type config: QALLMGeneratorConfig, optional
    :param cache_kvdriver_config: Конфигурация структуры данных для кеширования промежуточных результатов в рамках компонент данного класса. Значение по умолчению None.
    :type cache_kvdriver_config: Union[KeyValueDriverConfig, None], optional
    :param cache_llm_inference: Если True, то все результаты решения атомарных LLM-задач будут кешироваться, иначе False. Значение по умолчанию True.
    :type cache_llm_inference: bool, optional
    """

    def __init__(self, agent: AbstractAgentConnector, config: QALLMGeneratorConfig = QALLMGeneratorConfig(),
                 cache_kvdriver_config: Union[None, KeyValueDriverConfig] = None, cache_llm_inference: bool = True) -> None:
        self.config = config

        self.cachekv = self.init_cachekv(
            cache_kvdriver_config, config.cache_table_name)

        self.agent = agent
        ag_task_cache_config = None
        if cache_llm_inference:
            ag_task_cache_config = deepcopy(cache_kvdriver_config)

        self.answer_generator_solver = AgentTaskSolver(
            self.agent, self.config.ag_task_config, ag_task_cache_config)

        self.log = self.config.log
        self.verbose = self.config.verbose

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
            if self.answer_generator_solver.cachekv is not None:
                self.answer_generator_solver.cachekv.clear()

    def get_cache_key(self, query: str, context_triplets: List[Triplet]) -> List[object]:
        str_triplets = hashlib.sha1("\n".join(sorted([TripletCreator.stringify(
            triplet)[1] for triplet in context_triplets])).encode()).hexdigest()
        str_using_agent_info = f"{self.agent.CONNECTOR_KW}:{self.agent.config.to_str()}"
        return [self.config.to_str(), str_using_agent_info, query, str_triplets]

    @CacheUtils.cache_method_output
    def generate(self, query: str, context_triplets: List[Triplet]) -> Tuple[str, ReturnInfo]:
        """Метод предназначен для условной генерации ответа на вопрос.

        :param query: Вопрос на естественном языке.
        :type query: str
        :param context: Ненумерованный список дополнительной информации на естественном языке для генерации ответа.
        :type context: str
        :return: Кортеж из двух объектов: (1) сгенерированный ответ на вопрос; (2) статус выполнения операции с пояснительной информацией.
        :rtype: Tuple[str, ReturnInfo]
        """

        rinfo = ReturnInfo()
        self.log("START ANSWER GENERATION ...", verbose=self.config.verbose)
        self.log(
            f"BASE_QUESTION ID: {create_id(query)}", verbose=self.config.verbose)
        self.log(f"BASE_QUESTION: {query}", verbose=self.config.verbose)
        self.log(f"CONTEXT_TRIPLETS:", verbose=self.config.verbose)
        for triplet in context_triplets:
            self.log(f"*[{triplet.id}] {triplet}", verbose=self.config.verbose)

        self.log("Выполнение условной генерации ответа на вопрос с помощью LLM-агента...",
                 verbose=self.config.verbose)
        answer, status = self.answer_generator_solver.solve(
            lang=self.config.lang, gen_strategy=self.config.agent_gen_stategy,
            query=query, triplets=context_triplets)

        if status != ReturnStatus.success:
            rinfo.occurred_warning.append(status)

        if answer is None or len(answer) == 0:
            rinfo.status = ReturnStatus.empty_answer
            rinfo.message = STATUS_MESSAGE[rinfo.status]
        else:
            self.log(
                f"RESULT:\n* GENERATED ANSWER - {answer}", verbose=self.config.verbose)

        self.log(f"STATUS: {rinfo.status}", verbose=self.config.verbose)

        return answer, rinfo
