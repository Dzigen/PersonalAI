from .configs import QA_MAIN_LOG_PATH
from ...kg_model import KnowledgeGraphModel
from ...utils import Logger, ReturnStatus, ReturnInfo
from ...utils.data_structs import create_id
from ...utils.errors import STATUS_MESSAGE

from dataclasses import dataclass, field
from typing import Tuple

@dataclass
class QAPipelineConfig:
    """Конфигурация QA-конвейера.

    :param query_parser_config: Конфигурация первой стадии QA-конвейера: извлечение сущностей из user-вопроса. Значение по умолчанию QueryLLMParserConfig().
    :type query_parser_config: QueryLLMParserConfig
    :param knowledge_comparator_config: Конфигурация второй стадии QA-конвейера: сопоставление (match) сущностей из user-вопроса с информацией в графе знаний. Значение по умолчанию KnowledgeComparatorConfig().
    :type knowledge_comparator_config: KnowledgeComparatorConfig
    :param knowledge_retriever_config: Конфигурация третьей стадии QA-конвейера: извлечение релевантной информации из графа знаний для user-вопроса. Значение по умолчанию KnowledgeRetrieverConfig().
    :type knowledge_retriever_config: KnowledgeRetrieverConfig
    :param answer_generator_config: Конфигурация четвёртой стадии QA-конвейера: условная генерация ответа на user-вопрос. Значение по умолчанию QALLMGeneratorConfig().
    :type answer_generator_config: QALLMGeneratorConfig
    :param log: Отладочный класс для журналирования/мониторинга поведения инициализируемой компоненты. Значение по умолчанию Logger(LOG_PATH).
    :type log: Logger
    :param verbose: Если True, то информация о поведении класса будет сохраняться в stdout и файл-журналирования (log), иначе только в файл. Значение по умолчанию False.
    :type verbose: bool
    """
    # query_parser_config: QueryLLMParserConfig = field(default_factory=lambda: QueryLLMParserConfig())
    # knowledge_comparator_config: KnowledgeComparatorConfig = field(default_factory=lambda: KnowledgeComparatorConfig())
    # knowledge_retriever_config: KnowledgeRetrieverConfig = field(default_factory=lambda: KnowledgeRetrieverConfig())
    # answer_generator_config: QALLMGeneratorConfig = field(default_factory=lambda: QALLMGeneratorConfig())
    # log: Logger = field(default_factory=lambda: Logger(QA_MAIN_LOG_PATH))
    # verbose: bool = False

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

        # self.query_parser = QueryLLMParser(self.config.query_parser_config)
        # self.knowledge_comparator = KnowledgeComparator(self.kg_model, self.config.knowledge_comparator_config)
        # self.knowledge_retriever = KnowledgeRetriever(self.kg_model, self.config.knowledge_retriever_config)
        # self.answer_generator = QALLMGenerator(self.config.answer_generator_config)

    def answer(self, query: str) -> Tuple[str, ReturnInfo]:
        """Метод предназначен для генерации ответа на user-вопрос. Ответ обуславливается на информацию из имеющегося графа знаний.

        :param query: User-вопрос на естественном языке.
        :type query: str
        :return: Кортеж из двух объектов: (1) cгенерированный ответ; (2) статус завершения операции с пояснительной информацией.
        :rtype: Tuple[str, ReturnInfo]
        """

        pass
