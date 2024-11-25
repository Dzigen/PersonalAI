from typing import List, Tuple
from dataclasses import dataclass, field

from .configs import DEFAULT_ANSWER_GEN_TASK_CONFIG, QA_MAIN_LOG_PATH

from ....utils.data_structs import Triplet, TripletCreator, RelationType
from ....utils.errors import STATUS_MESSAGE
from ....agents import AgentDriver, AgentDriverConfig
from ....utils import Logger, detect_lang, ReturnInfo, ReturnStatus, AgentTaskSolverConfig, AgentTaskSolver

@dataclass
class QALLMGeneratorConfig:
    """Конфигурация "Question Answering"-стадии.

    :param lang: Язык, который будет использоваться в подаваемом на вход тексте. На основании выбранного языка будут использоваться соответствующие промпты. Если 'auto', то язык определяется автоматически. Значение по умолчанию 'auto'.
    :type lang: str
    :param system_prompt: System-промпт с описание персоны, свойствам которой должен удовлетворять LLM-агент при генерации оветов.
    :type system_prompt: dict
    :param user_prompt: User-промпт для LLM-агента с описанием QA-задачи.
    :type user_prompt: dict
    :param answer_parse_func: Функция разбора результатов генерации LLM-агента.
    :type answer_parse_func: dict
    :param agent_cofig: Конфигурация LLM-агента, который будет использоваться в рамках данной стадии. Значение по умолчанию AgentDriverConfig().
    :type agent_cofig: AgentDriverConfig
    :param relation_type: Типы триплетов, которые могут присутствовать в контексте для генерации ответа на user-вопрос. Значение по умолчанию [RelationType.simple, RelationType.hyper, RelationType.episodic].
    :type relation_type: List[RelationType]
    :param log: Отладочный класс для журналирования/мониторинга поведения инициализируемой комопненты. Значение по умолчанию Logger(QA_LOG_PATH).
    :type log: Logger
    :param verbose: Если True, то информация о поведении класса будет сохраняться в stdout и файл-журналирования (log), иначе только в файл. Значение по умолчанию False.
    :type verbose: bool
    """
    lang: str = "auto"
    agent_cofig: AgentDriverConfig = field(default_factory=lambda: AgentDriverConfig())
    ag_task_config: AgentTaskSolverConfig = field(default_factory=DEFAULT_ANSWER_GEN_TASK_CONFIG)

    relation_type: List[RelationType] = field(default_factory=lambda: [RelationType.simple, RelationType.hyper, RelationType.episodic])

    log: Logger = field(default_factory=lambda: Logger(QA_MAIN_LOG_PATH))
    verbose: bool = False

class QALLMGenerator:
    """Верхнеуровневый класс четвёртой стадии QA-конвейера для генерации ответа на user-вопрос,
    обусловленного извлёчённой информацией из памяти (графа знаний) ассистента.

    :param config: Конфигурация "Answer-generation"-стадии. Значение по умолчанию QALLMGeneratorConfig().
    :type config: QALLMGeneratorConfig
    """
    def __init__(self, config: QALLMGeneratorConfig = QALLMGeneratorConfig()) -> None:
        self.config = config
        self.log = self.config.log

        self.agent = AgentDriver.connect(config.agent_cofig)
        self.answer_generator_solver = AgentTaskSolver(self.config.ag_task_config)

    def generate(self, query: str, context_triplets: List[Triplet]) -> Tuple[str, ReturnInfo]:
        """Метод предназначен для условной генерации ответа на вопрос.

        :param query: Вопрос на естественном языке.
        :type query: str
        :param context: Ненумерованный список дополнительной информации на естественном языке для генерации ответа.
        :type context: str
        :return: Кортеж из двух объектов: (1) сгенерированнвй ответ на вопрос; (2) статус выполнения операции с пояснительной информацией.
        :rtype: Tuple[str, ReturnInfo]
        """

        info = ReturnInfo()
        self.log("="*20, verbose=self.config.verbose)
        self.log(f"Входные данные:", verbose=self.config.verbose)
        self.log(f"\tQUERY: {query}", verbose=self.config.verbose)
        self.log(f"\tCONTEXT_TRIPLETS: {context_triplets}", verbose=self.config.verbose)

        self.log("Выполнение условной генерации ответа на вопрос с помощью LLM-агента...", verbose=self.config.verbose)
        answer, status = self.answer_generator_solver.solve(query=query, triplets=context_triplets)
        self.log(f"Результат:\n{answer}")
        self.log(f"Статус: {STATUS_MESSAGE[status]}")

        if status != ReturnStatus.success:
            info.occurred_warning.append(status)

        if len(answer) == 0:
            info.status = ReturnStatus.empty_answer
            info.message = STATUS_MESSAGE[info.status]

        return answer, info
