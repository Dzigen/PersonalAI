from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Union

from .kg_model import KnowledgeGraphModel, KnowledgeGraphModelConfig
from .pipelines.qa import QAPipeline, QAPipelineConfig
from .pipelines.memorize import MemPipeline, MemPipelineConfig
from .utils import Logger, ReturnInfo, Triplet
from .utils.data_structs import create_id, BaseComponentConfig, LanguageConfig
from .db_drivers.kv_driver import KeyValueDriverConfig
from .config import PAI_MAIN_LOG_PATH, DEFAULT_PERSONALAI_KVCACHE_CONFIG
from .utils.agent_stat_analyzer import AgentStatAnalyzerConfig


@dataclass
class PersonalAIConfig(BaseComponentConfig, LanguageConfig):
    """Конфигурация персонального ассистента.

    :param kg_model_config: Конфигурация памяти ассистента. Значение по умолчанию KnowledgeGraphModelConfig().
    :type kg_model_config: KnowledgeGraphModelConfig, optional
    :param qa_pipeline_config: Конфигурация конвейера, который выполняет обработку входящих user-вопросов, поиск релевантной информации в памяти асситента и генерацию ответов. Значение по умолчанию QAPipelineConfig().
    :type qa_pipeline_config: QAPipelineConfig, optional
    :param mem_pipeline_config: Конфигурация конвейера, который выполняет изменение/обновление информации/знаний в памяти ассистента. Значение по умолчанию MemPipelineConfig().
    :type mem_pipeline_config: MemPipelineConfig, optional
    """
    kg_model_config: KnowledgeGraphModelConfig = field(
        default_factory=lambda: KnowledgeGraphModelConfig())
    qa_pipeline_config: QAPipelineConfig = field(
        default_factory=lambda: QAPipelineConfig())
    mem_pipeline_config: MemPipelineConfig = field(
        default_factory=lambda: MemPipelineConfig())

    log: Logger = field(default_factory=lambda: Logger(PAI_MAIN_LOG_PATH))


class PersonalAI:
    """Верхнеуровневый класс (точка входа) персонального ассистента.

    :param config: Конфигурация персонального ассистента. Значение по умолчанию PersonalAIConfig().
    :type config: PersonalAIConfig, optional
    :param cache_kvdriver_config: Конфигурация структуры данных для кеширования результатов промежуточных операций ассистента. Значение по умолчанию None.
    :type cache_kvdriver_config: Union[None,KeyValueDriverConfig], optional
    :param inferencestat_config: Конфигурация компоненты для сбора информации и расчёта статистик по результатам выполнения inference-операциий в рамках LLM-задач. Значение по умолчанию None.
    :type inferencestat_config: Union[None, AgentStatAnalyzerConfig], optional
    """

    def __init__(self, config: PersonalAIConfig = PersonalAIConfig(),
                 cache_kvdriver_config: Union[None, KeyValueDriverConfig] = DEFAULT_PERSONALAI_KVCACHE_CONFIG,
                 inferencestat_config: Union[None, AgentStatAnalyzerConfig] = AgentStatAnalyzerConfig()) -> None:

        config.synchronize_language()

        self.kg_model = KnowledgeGraphModel(
            config.kg_model_config, cache_kvdriver_config)
        self.qa_pipeline = QAPipeline(
            self.kg_model, config.qa_pipeline_config,
            cache_kvdriver_config, inferencestat_config)
        self.mem_pipeline = MemPipeline(
            self.kg_model, config.mem_pipeline_config,
            cache_kvdriver_config, inferencestat_config)

        self.log = config.log
        self.verbose = config.verbose

    def answer_question(self, question: str) -> Tuple[str, ReturnInfo]:
        """Метод предназначен для контекстуального поиска и извлечения релевантной информации
        из памяти (графа знаний) ассистента для генерации ответа на user-вопрос.

        :param question: User-вопрос на естественном языке.
        :type question: str
        :return: Кортеж из двух объектов: (1) сгенерированный ответ; (2) статус завершения операции с пояснительной информацией.
        :rtype: Tuple[str, ReturnInfo]
        """
        self.log("START ANSWER GENERATION...", verbose=self.verbose)
        self.log(
            f"BASE_QUESTION ID: {create_id(question)}", verbose=self.verbose)
        self.log(f"BASE_QUESTION: {question}", verbose=self.verbose)

        answer, info = self.qa_pipeline.answer(question)
        self.log(f"RESULT:\n* FINAL ANSWER - {answer}", verbose=self.verbose)
        return answer, info

    def update_memory(self, text: str, text_properties: Union[None, Dict] = None) -> Tuple[List[Triplet], ReturnInfo]:
        """Метод предназначен для добавления новой информации в память (граф знаний) и её актуализацию.

        :param text: Слабоструктурированный текст на естественном языке.
        :type text: str
        :param text_properties: Набор свойств данного текста, который необходимо дополнительно сохранить в память ассистента и сопоставить соответствующим фрагментам информации. Значение по умолчанию None.
        :type text_properties: Union[None, Dict], optional
        :return: Кортеж из двух объектов: (1) список извлечённой из текста информации (в виде триплетов), который использовался для обновления/актуализации памяти ассистента; (2) статус завершения операции с пояснительной информацией.
        :rtype: Tuple[List[Triplet], ReturnInfo]
        """
        self.log("START MEMORY_UPDATING ...", verbose=self.verbose)
        self.log(f"BASE_TEXT ID: {create_id(text)}", verbose=self.verbose)
        self.log(f"BASE_TEXT: {text}", verbose=self.verbose)
        self.log(f"PROPERTIES: {text_properties}", verbose=self.verbose)

        triplets, info = self.mem_pipeline.remember(text, text_properties)
        self.log(
            f"RESULT:\n* EXTRACTED_TRIPLETS AMOUNT - {len(triplets)}", verbose=self.verbose)

        return triplets, info

    def __del__(self):
        # print("deleting PersonalAI-class")
        del self.kg_model
        del self.qa_pipeline
        del self.mem_pipeline
