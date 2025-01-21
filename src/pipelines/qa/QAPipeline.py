from .configs import QA_MAIN_LOG_PATH
from .kg_reasoning import KnowledgeGraphReasonerConfig, KnowledgeGraphReasoner
from ...kg_model import KnowledgeGraphModel
from ...utils import Logger, ReturnStatus, ReturnInfo
from ...utils.data_structs import create_id
from ...utils.errors import STATUS_MESSAGE

from dataclasses import dataclass, field
from typing import Tuple

@dataclass
class QAPipelineConfig:
    """

    :param log: Отладочный класс для журналирования/мониторинга поведения инициализируемой компоненты. Значение по умолчанию Logger(LOG_PATH).
    :type log: Logger
    :param verbose: Если True, то информация о поведении класса будет сохраняться в stdout и файл-журналирования (log), иначе только в файл. Значение по умолчанию False.
    :type verbose: bool
    """
    reasoner_config: KnowledgeGraphReasonerConfig = field(default_factory=lambda: KnowledgeGraphReasonerConfig())
    log: Logger = field(default_factory=lambda: Logger(QA_MAIN_LOG_PATH))
    verbose: bool = False

class QAPipeline:
    """Верхнеуровневый класс QA-конвейера, отвечающий за генерацию ответов на вопросы.

    :param kg_model: Модель памяти (графа знаний) ассистента.
    :type kg_model: KnowledgeGraphModel
    :param config: Конфигурация QA-конвейера. Значение по умолчанию QAPipelineConfig().
    :type config: QAPipelineConfig
    """

    def __init__(self, kg_model: KnowledgeGraphModel, config: QAPipelineConfig = QAPipelineConfig()) -> None:
        self.config = config
        self.kg_model = kg_model
        self.log = config.log

        self.query_enhancement = ... # TODO
        self.kg_reasoner = KnowledgeGraphReasoner(kg_model, self.config.reasoner_config)
        self.knowledge_summarizer = ... # TODO

    def answer(self, query: str) -> Tuple[str, ReturnInfo]:
        """Метод предназначен для генерации ответа на user-вопрос. Ответ обуславливается на информацию из имеющегося графа знаний.

        :param query: User-вопрос на естественном языке.
        :type query: str
        :return: Кортеж из двух объектов: (1) cгенерированный ответ; (2) статус завершения операции с пояснительной информацией.
        :rtype: Tuple[str, ReturnInfo]
        """

        answer, info = self.kg_reasoner.perform(query)
        return answer, info
