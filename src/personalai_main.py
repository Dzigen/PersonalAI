from dataclasses import dataclass, field
from typing import List, Dict, Tuple
from tqdm import tqdm

from .kg_model import GraphModelConfig, EmbeddingsModelConfig, KnowledgeGraphModel
from .pipelines.qa import QAPipeline, QAPipelineConfig
from .pipelines.memorize import MemPipeline, MemPipelineConfig
from .utils import Logger, ReturnInfo, Triplet

RKG_LOG_PATH = "log/personalai"

@dataclass
class PersonalAIConfig:
    """Конфигурация персонального ассистента.

    :param graph_struct_config: Конфигурация модели, которая отвечает за представление знаний ассистента в графовом формате. Значение по умолчанию GraphModelConfig().
    :type graph_struct_config: GraphModelConfig
    :param embedds_struct_config: Конфигурация модели, которая отвечает за предтсавление знаний ассистента в векторном формате. Значение по умолчанию EmbeddingsModelConfig().
    :type embedds_struct_config: EmbeddingsModelConfig
    :param qa_pipeline_config: Конфигурация конвейера, который выполняет генерацию ответов на вопросы. Значение по умолчанию QAPipelineConfig().
    :type qa_pipeline_config: QAPipelineConfig
    :param mem_pipeline_config: Конфигурация конвейера, который выполняет изменение/обновление знаний в памяти ассистента. Значение по умолчанию MemPipelineConfig().
    :type mem_pipeline_config: MemPipelineConfig
    :param log: Отладочный класс для журналирования/мониторинга поведения инициализируемой комопненты. Значение по умолчанию Logger(RKG_LOG_PATH).
    :type log: Logger
    :param verbose: Если True, то информация о поведении класса будет сохраняться в stdout и файл-журналирования (log), иначе только в файл. Значение по умолчанию False.
    :type verbose: bool
    """
    graph_struct_config: GraphModelConfig = field(default_factory=lambda: GraphModelConfig())
    embedds_struct_config: EmbeddingsModelConfig = field(default_factory=lambda: EmbeddingsModelConfig())
    qa_pipeline_config: QAPipelineConfig = field(default_factory=lambda: QAPipelineConfig())
    mem_pipeline_config: MemPipelineConfig = field(default_factory=lambda: MemPipelineConfig())
    log: Logger = field(default_factory=lambda:Logger(RKG_LOG_PATH))
    verbose: bool = False

class PersonalAI:
    """Верхнеуровневый класс персонального ассистента.

    :param config: Конфигурация персонального ассистента.
    :type config: PersonalAIConfig
    """
    def __init__(self, config: PersonalAIConfig):
        self.config = config
        self.log = self.config.log

        self.kg_model = KnowledgeGraphModel(
            graph_config=config.graph_struct_config,
            embeddings_config=config.embedds_struct_config)
        self.qa_pipeline = QAPipeline(kg_model=self.kg_model, config=config.qa_pipeline_config)
        self.mem_pipeline = MemPipeline(kg_model=self.kg_model, config=config.mem_pipeline_config)

    def answer_question(self, question: str) -> Tuple[str, ReturnInfo]:
        """Метод предназанчен для контекстуального поиска и извлечения релевантной информации
        из памяти (графа знаний) ассистента для генерации ответа на user-вопрос.

        :param question: User-вопрос на естественном языке.
        :type question: str
        :return: Кортеж из двух объектов: (1) сгенерированный ответ; (2) статус завершения операции с пояснительной информацией.
        :rtype: Tuple[str, ReturnInfo]
        """
        self.log("Start answer generation:", verbose=self.config.verbose)
        self.log(f"\t- question: {question}", verbose=self.config.verbose)
        answer, info = self.qa_pipeline.answer(question)
        self.log(f"\t- answer: {answer}", verbose=self.config.verbose)
        return answer, info

    def update_memory(self, text: str, text_properties: Dict) -> Tuple[List[Triplet], ReturnInfo]:
        """Метод предназначен для добавления новой информации в память (граф знаний) и её актуализацию.

        :param text: Слабоструктурированный текст на естественном языке.
        :type text: str
        :param text_properties: Набор свойств данного текста, который необходимо дополнительно сохранить в память ассистента.
        :type text_properties: Dict
        :return: Кортеж из двух объектов: (1) список извлечённой из текста информации (в виде триплетов), который использовался для обновления/актуализации памяти ассистента; (2) статус завершения операции с пояснительной информацией.
        :rtype: Tuple[List[Triplet], ReturnInfo]
        """
        self.log("Start memory-updating...", verbose=self.config.verbose)
        triplets, info = self.mem_pipeline.remember(text, text_properties)
        self.log(f"\t- triplets amount: {len(triplets)}", verbose=self.config.verbose)
        return triplets, info
