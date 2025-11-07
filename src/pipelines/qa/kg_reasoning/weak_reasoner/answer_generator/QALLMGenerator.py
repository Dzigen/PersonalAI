from typing import List, Tuple, Union, Dict
from dataclasses import dataclass, field
from copy import deepcopy
import hashlib

from .configs import AG_MAIN_LOG_PATH
from .utils import WeakAGeneratorTaskSolvers, QALLMGeneratorAgentTasksConfig
from ......utils.data_structs import Triplet, RelationType, create_id, TripletCreator, \
    BaseComponentConfig, LanguageConfig, RELATIONS_TYPES_MAP
from ......utils.errors import STATUS_MESSAGE
from ......agents.utils import AbstractAgentConnector
from ......utils import Logger, ReturnInfo, ReturnStatus, AgentTaskSolver
from ......utils.cache_kv import CacheUtils
from ......db_drivers.kv_driver import KeyValueDriverConfig
from ......utils.agent_stat_analyzer import AgentStatAnalyzerConfig
from ......utils.cache_kv.CacheOperations import CacheOperations
from ......utils.agent_stat_analyzer.AgentStatOperations import AgentStatOperations


@dataclass
class QALLMGeneratorConfig(BaseComponentConfig, LanguageConfig):
    """Конфигурация "Question Answering"-стадии QA-конвейера.

    :param agent_gen_stategy: Стратегия генерации текста для используемого LLM-агента. В случае None-значение будет использоваться стратегия по умолчанию. Значение по умолчанию None.
    :type agent_gen_stategy: Union[None,Dict[str, Union[str, int, float]]], optional
    :param agent_tasks_config: Конфигурации LLM-промптом для решения заданных задач с помощью LLM-агента. Значение по умолчанию QALLMGeneratorAgentTasksConfig().
    :type agent_tasks_config: Union[QALLMGeneratorAgentTasksConfig,Dict], optional
    :param relation_type: Типы триплетов, которые могут присутствовать в контексте для генерации ответа на user-вопрос. Значение по умолчанию [RelationType.hyper].
    :type relation_type: List[RelationType], optional
    :param cache_table_name: Название таблицы в структуре (базе) данных, куда будут сохраняться (кешироваться) основные результаты работы QALLMGenerator-класса. Значение по умолчанию 'qa_agenerator_stage_cache'.
    :type cache_table_name: str, optional
    """
    agent_gen_stategy: Union[None, Dict[str, Union[str, int, float]]] = None
    agent_tasks_config: Union[QALLMGeneratorAgentTasksConfig, Dict] = field(default_factory=lambda: QALLMGeneratorAgentTasksConfig())

    relation_type: List[Union[str, RelationType]] = field(default_factory=lambda: [RelationType.hyper, RelationType.simple])

    cache_table_name: Union[str, None] = 'qa_agenerator_stage_cache'
    log: Logger = field(default_factory=lambda: Logger(AG_MAIN_LOG_PATH))

    def to_str(self):
        str_relations = ";".join(
            list(map(lambda v: v.value if isinstance(v, RelationType) else v, self.relation_type)))
        return f"{self.lang}|{self.agent_gen_stategy}|{self.agent_tasks_config.to_str()}|{str_relations}"

    @staticmethod
    def from_dict(dict_config: Dict):
        formated_config = QALLMGeneratorConfig(**dict_config)
        formated_config.formate_fields()
        return formated_config

    def formate_fields(self) -> None:
        for i, rel_type in enumerate(self.relation_type):
            if not isinstance(rel_type, RelationType):
                self.relation_type[i] = RELATIONS_TYPES_MAP[rel_type]

        if isinstance(self.agent_tasks_config, dict):
            self.agent_tasks_config = QALLMGeneratorAgentTasksConfig.from_dict(self.agent_tasks_config)


class QALLMGenerator(CacheUtils, CacheOperations, AgentStatOperations):
    """Верхнеуровневый класс четвёртой стадии QA-конвейера для генерации ответа на user-вопрос,
    обусловленного извлечённой информацией из памяти (графа знаний) ассистента.

    :param agent: Коннектор к конкретному LLM-агенту для выполнения inference-операций.
    :type agent: AbstractAgentConnector
    :param config: Конфигурация "Answer-generation"-стадии. Значение по умолчанию QALLMGeneratorConfig().
    :type config: Union[QALLMGeneratorConfig,Dict], optional
    :param cache_kvdriver_config: Конфигурация структуры данных для кеширования промежуточных результатов в рамках компонент данного класса. Значение по умолчению None.
    :type cache_kvdriver_config: Union[KeyValueDriverConfig, None], optional
    :param inferencestat_config: Конфигурация компоненты для сбора информации и расчёта статистик по результатам выполнения inference-операциий в рамках LLM-задач. Значение по умолчанию None.
    :type inferencestat_config: Union[None, AgentStatAnalyzerConfig], optional
    :param cache_llm_inference: Если True, то все результаты решения атомарных LLM-задач будут кешироваться, иначе False. Значение по умолчанию True.
    :type cache_llm_inference: bool, optional
    """

    def __init__(self, agent: AbstractAgentConnector, config: Union[QALLMGeneratorConfig, Dict] = QALLMGeneratorConfig(),
                 cache_kvdriver_config: Union[None, KeyValueDriverConfig] = None,
                 inferencestat_config: Union[None, AgentStatAnalyzerConfig] = None,
                 cache_llm_inference: bool = True) -> None:
        if isinstance(config, dict):
            config: QALLMGeneratorConfig = QALLMGeneratorConfig.from_dict(config)
        else:
            config.formate_fields()
        self.config = config
        self.config.agent_tasks_config.versions_to_configs()

        self.cachekv = self.init_cachekv(
            cache_kvdriver_config, config.cache_table_name)

        self.agent = agent
        ag_task_cache_config = None
        if cache_llm_inference:
            ag_task_cache_config = deepcopy(cache_kvdriver_config)

        self.tasks_solvers: WeakAGeneratorTaskSolvers = WeakAGeneratorTaskSolvers(
            answer_generator_solver=AgentTaskSolver(
                self.agent, self.config.agent_tasks_config.ag, ag_task_cache_config, inferencestat_config)
        )

        self.log = self.config.log
        self.verbose = self.config.verbose

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

        self.log("Выполнение условной генерации ответа на вопрос с помощью LLM-агента...", verbose=self.config.verbose)
        answer, status = self.tasks_solvers.answer_generator_solver.solve(
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
