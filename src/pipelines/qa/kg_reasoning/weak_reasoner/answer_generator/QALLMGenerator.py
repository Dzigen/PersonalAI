from typing import List, Tuple
from dataclasses import dataclass, field

from .configs import DEFAULT_ANSWER_GEN_TASK_CONFIG, QA_MAIN_LOG_PATH

from ......utils.data_structs import Triplet, RelationType, create_id
from ......utils.errors import STATUS_MESSAGE
from ......agents import AgentDriver, AgentDriverConfig
from ......utils import Logger, ReturnInfo, ReturnStatus, AgentTaskSolverConfig, AgentTaskSolver

@dataclass
class QALLMGeneratorConfig:
    """Конфигурация "Question Answering"-стадии QA-конвейера.

    :param lang: Язык, который будет использоваться в подаваемом на вход тексте. На основании выбранного языка будут использоваться соответствующие промпты для инференса LLM-агента. Если 'auto', то язык определяется автоматически. Значение по умолчанию 'auto'.
    :type lang: str
    :param agent_cofig: Конфигурация LLM-агента, который будет использоваться в рамках данной стадии. Значение по умолчанию AgentDriverConfig().
    :type agent_cofig: AgentDriverConfig
    :param ag_task_config: Конфигурация атомарной задачи для LLM-агента по условной генерации ответа на вопрос.
    :type ag_tasK_config: AgentTaskSolverConfig
    :param relation_type: Типы триплетов, которые могут присутствовать в контексте для генерации ответа на user-вопрос. Значение по умолчанию [RelationType.simple, RelationType.hyper, RelationType.episodic].
    :type relation_type: List[RelationType]
    :param log: Отладочный класс для журналирования/мониторинга поведения инициализируемой компоненты. Значение по умолчанию Logger(QA_LOG_PATH).
    :type log: Logger
    :param verbose: Если True, то информация о поведении класса будет сохраняться в stdout и файл-журналирования (log), иначе только в файл. Значение по умолчанию False.
    :type verbose: bool
    """
    lang: str = "auto"
    agent_cofig: AgentDriverConfig = field(default_factory=lambda: AgentDriverConfig())
    ag_task_config: AgentTaskSolverConfig = field(default_factory=lambda: DEFAULT_ANSWER_GEN_TASK_CONFIG)

    relation_type: List[RelationType] = field(default_factory=lambda: [RelationType.simple, RelationType.hyper, RelationType.episodic])

    log: Logger = field(default_factory=lambda: Logger(QA_MAIN_LOG_PATH))
    verbose: bool = False

class QALLMGenerator:
    """Верхнеуровневый класс четвёртой стадии QA-конвейера для генерации ответа на user-вопрос,
    обусловленного извлечённой информацией из памяти (графа знаний) ассистента.

    :param config: Конфигурация "Answer-generation"-стадии. Значение по умолчанию QALLMGeneratorConfig().
    :type config: QALLMGeneratorConfig
    """
    def __init__(self, config: QALLMGeneratorConfig = QALLMGeneratorConfig()) -> None:
        self.config = config
        self.log = self.config.log

        self.agent = AgentDriver.connect(config.agent_cofig)
        self.answer_generator_solver = AgentTaskSolver(self.agent, self.config.ag_task_config)

    def generate(self, query: str, context_triplets: List[Triplet]) -> Tuple[str, ReturnInfo]:
        """Метод предназначен для условной генерации ответа на вопрос.

        :param query: Вопрос на естественном языке.
        :type query: str
        :param context: Ненумерованный список дополнительной информации на естественном языке для генерации ответа.
        :type context: str
        :return: Кортеж из двух объектов: (1) сгенерированный ответ на вопрос; (2) статус выполнения операции с пояснительной информацией.
        :rtype: Tuple[str, ReturnInfo]
        """

        info = ReturnInfo()
        self.log("START ANSWER GENERATION ...", verbose=self.config.verbose)
        self.log(f"BASE_QUESTION ID: {create_id(query)}", verbose=self.config.verbose)
        self.log(f"BASE_QUESTION: {query}", verbose=self.config.verbose)
        self.log(f"CONTEXT_TRIPLETS:",verbose=self.config.verbose)
        for triplet in context_triplets:
            self.log(f"*[{triplet.id}] {triplet}", verbose=self.config.verbose)

        self.log("Выполнение условной генерации ответа на вопрос с помощью LLM-агента...", verbose=self.config.verbose)
        answer, status = self.answer_generator_solver.solve(lang=self.config.lang, query=query, triplets=context_triplets)

        if status != ReturnStatus.success:
            info.occurred_warning.append(status)

        if answer is None or len(answer) == 0:
            info.status = ReturnStatus.empty_answer
            info.message = STATUS_MESSAGE[info.status]

        self.log(f"RESULT:\n* GENERATED ANSWER - {answer}", verbose=self.config.verbose)
        self.log(f"STATUS: {STATUS_MESSAGE[info.status]}", verbose=self.config.verbose)

        return answer, info
