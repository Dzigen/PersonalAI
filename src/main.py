from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Union
from copy import deepcopy

from .kg_model import KnowledgeGraphModel, KnowledgeGraphModelConfig
from .pipelines.qa import QAPipeline, QAPipelineConfig
from .pipelines.memorize import MemPipeline, MemPipelineConfig
from .utils import Logger, ReturnInfo, Triplet
from .utils.data_structs import create_id, BaseComponentConfig, LanguageConfig
from .db_drivers.kv_driver import KeyValueDriverConfig
from .config import PAI_MAIN_LOG_PATH, DEFAULT_PERSONALAI_KVCACHE_CONFIG
from .utils.agent_stat_analyzer import AgentStatAnalyzerConfig
from .TextIdStore import TextIdStoreConfig, TextIdStore


@dataclass
class PersonalAIConfig(BaseComponentConfig, LanguageConfig):
    """Конфигурация персонального ассистента.

    :param kg_model_config: Конфигурация памяти ассистента. Значение по умолчанию KnowledgeGraphModelConfig().
    :type kg_model_config: Union[KnowledgeGraphModelConfig, Dict], optional
    :param qa_pipeline_config: Конфигурация конвейера, который выполняет обработку входящих user-вопросов, поиск релевантной информации в памяти ассистента и генерацию ответов. Значение по умолчанию QAPipelineConfig().
    :type qa_pipeline_config: Union[QAPipelineConfig, Dict], optional
    :param mem_pipeline_config: Конфигурация конвейера, который выполняет изменение/обновление информации/знаний в памяти ассистента. Значение по умолчанию MemPipelineConfig().
    :type mem_pipeline_config: Union[MemPipelineConfig, Dict], optional
    :param textidstore_config: Конфигурация хранилища отображений между исходными текстами (сохранёнными в модель памяти) и извлечёнными (из данных текстов) триплетами. Значение по умолчанию TextIdStoreConfig().
    :type textidstore_config: Union[TextIdStoreConfig, Dict], optional
    """
    kg_model_config: Union[KnowledgeGraphModelConfig, Dict] = field(default_factory=lambda: KnowledgeGraphModelConfig())
    qa_pipeline_config: Union[QAPipelineConfig, Dict] = field(default_factory=lambda: QAPipelineConfig())
    mem_pipeline_config: Union[MemPipelineConfig, Dict] = field(default_factory=lambda: MemPipelineConfig())
    textidstore_config: Union[TextIdStoreConfig, Dict] = field(default_factory=lambda: TextIdStoreConfig())

    log: Logger = field(default_factory=lambda: Logger(PAI_MAIN_LOG_PATH))

    def to_str(self):
        # TODO
        raise NotImplementedError

    @staticmethod
    def from_dict(dict_config: Dict):
        dictconfig_copy = deepcopy(dict_config)
        formated_config = PersonalAIConfig(**dictconfig_copy)
        formated_config.formate_fields()
        return formated_config

    def formate_fields(self):
        if isinstance(self.kg_model_config, dict):
            self.kg_model_config = KnowledgeGraphModelConfig.from_dict(self.kg_model_config)
        else:
            self.kg_model_config.formate_fields()

        if isinstance(self.qa_pipeline_config, dict):
            self.qa_pipeline_config = QAPipelineConfig.from_dict(self.qa_pipeline_config)
        else:
            self.qa_pipeline_config.formate_fields()

        if isinstance(self.mem_pipeline_config, dict):
            self.mem_pipeline_config = MemPipelineConfig.from_dict(self.mem_pipeline_config)
        else:
            self.mem_pipeline_config.formate_fields()

        if isinstance(self.textidstore_config, dict):
            self.textidstore_config = TextIdStoreConfig.from_dict(self.textidstore_config)
        else:
            self.textidstore_config.formate_fields()


class PersonalAI:
    """Верхнеуровневый класс (точка входа) персонального ассистента.

    :param config: Конфигурация персонального ассистента. Значение по умолчанию PersonalAIConfig().
    :type config: Union[Dict,PersonalAIConfig], optional
    :param cache_kvdriver_config: Конфигурация структуры данных для кеширования результатов промежуточных операций ассистента. Значение по умолчанию DEFAULT_PERSONALAI_KVCACHE_CONFIG.
    :type cache_kvdriver_config: Union[None,KeyValueDriverConfig], optional
    :param inferencestat_config: Конфигурация компоненты для сбора информации и расчёта статистик по результатам выполнения inference-операциий в рамках LLM-задач. Значение по умолчанию AgentStatAnalyzerConfig().
    :type inferencestat_config: Union[None, AgentStatAnalyzerConfig], optional
    """

    def __init__(self, config: Union[Dict, PersonalAIConfig] = PersonalAIConfig(),
                 cache_kvdriver_config: Union[None, KeyValueDriverConfig] = DEFAULT_PERSONALAI_KVCACHE_CONFIG,
                 inferencestat_config: Union[None, AgentStatAnalyzerConfig] = AgentStatAnalyzerConfig()) -> None:
        if isinstance(config, dict):
            config: PersonalAIConfig = PersonalAIConfig.from_dict(config)
        else:
            config.formate_fields()
        config.synchronize_language()

        self.kg_model = KnowledgeGraphModel(
            config.kg_model_config, cache_kvdriver_config)
        self.qa_pipeline = QAPipeline(
            self.kg_model, config.qa_pipeline_config,
            cache_kvdriver_config, inferencestat_config)
        self.mem_pipeline = MemPipeline(
            self.kg_model, config.mem_pipeline_config,
            cache_kvdriver_config, inferencestat_config)

        self.textid_store = TextIdStore(config.textidstore_config)

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
        self.log(f"BASE_QUESTION ID: {create_id(question)}", verbose=self.verbose)
        self.log(f"BASE_QUESTION: {question}", verbose=self.verbose)

        answer, info = self.qa_pipeline.answer(question)
        self.log(f"RESULT:\n* FINAL ANSWER - {answer}", verbose=self.verbose)
        return answer, info

    def update_memory(self, text: str, text_properties: Union[None, Dict] = None, text_id: Union[None, str] = None) -> Tuple[str, List[Triplet], ReturnInfo]:
        """Метод предназначен для добавления новой информации в память (граф знаний) и её актуализации.

        :param text: Слабоструктурированный текст на естественном языке.
        :type text: str
        :param text_properties: Набор свойств данного текста, который необходимо дополнительно сохранить в память ассистента и сопоставить соответствующим фрагментам информации. Значение по умолчанию None.
        :type text_properties: Union[None, Dict], optional
        :param text_id: Идентификатор текста, сохраняемого в память.
        :type text_id: Union[None, str], optional
        :return: Кортеж из трёх объектов: (1) идентификатор данного 'text'-значения; (2) список извлечённой из текста информации (в виде триплетов), который использовался для обновления/актуализации памяти ассистента; (3) статус завершения операции с пояснительной информацией.
        :rtype: Tuple[List[Triplet], ReturnInfo]
        """
        self.log("START MEMORY_UPDATING ...", verbose=self.verbose)
        self.log(f"BASE_TEXT ID: {create_id(text)}", verbose=self.verbose)
        self.log(f"BASE_TEXT: {text}", verbose=self.verbose)
        self.log(f"PROPERTIES: {text_properties}", verbose=self.verbose)

        text_id = create_id() if text_id is None else text_id
        self.log(f"INTERNAL TEXT ID: {text_id}", verbose=self.verbose)
        if self.textid_store.textid_to_tripletsid_store.item_exist(text_id):
            raise ValueError("'text' with given 'text_id' already exists! Change 'text_id' value")

        triplets, info = self.mem_pipeline.remember(text, text_properties)
        self.textid_store.save_info(text_id, triplets)
        self.log(f"RESULT:\n* EXTRACTED_TRIPLETS AMOUNT - {len(triplets)}", verbose=self.verbose)

        return text_id, triplets, info

    def clear_memory(self, text_id: str) -> Dict[str, Dict[int, Dict[str, bool]]]:
        """Метод предназначен для удаления информации (представленной в виде набор триплетов) из модели памяти ассистента
        по идентификатору исходного неструктурированного фрагмента текста, из которого она (информация / набор триплетов) была извлечена.

        :param text_id: Идентификатор, с которым соответствующий текст на естественном языке был добавлен/сохранён в модель памяти ассистента.
        :type text_id: str
        :return: Словарь с информацией о триплетах (соответствуюих данному text_id), которые были удалены (значение True, иначе False) из памяти ассистента.
        :rtype: Dict[str, Dict[int,Dict[str,bool]]]
        """
        # получаем triplets id из kv-database
        triplets = self.textid_store.select_triplets_to_delete(text_id)
        # вызываем remove_knowledge у модели графа знаний
        delete_info = self.kg_model.remove_knowledge(triplets)
        # удаляем соответствующие записи из kv-database
        self.textid_store.clear_info(text_id)

        return delete_info

    def __del__(self):
        # print("deleting PersonalAI-class")
        try:
            del self.kg_model
        except AttributeError:
            pass
        try:
            del self.qa_pipeline
        except AttributeError:
            pass
        try:
            del self.mem_pipeline
        except AttributeError:
            pass
        try:
            del self.textid_store
        except AttributeError:
            pass
