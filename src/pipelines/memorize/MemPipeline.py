from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Union

from .configs import MEMORIZE_MAIN_LOG_PATH
from .extractor.LLMExtractor import LLMExtractor
from .updator.LLMUpdator import LLMUpdator
from .extractor import LLMExtractorConfig
from .updator import LLMUpdatorConfig
from .utils import MemPipelineStages
from ...kg_model import KnowledgeGraphModel
from ...utils import Logger, Triplet, ReturnStatus, ReturnInfo
from ...utils.data_structs import create_id, BaseComponentConfig, LanguageConfig
from ...utils.errors import STATUS_MESSAGE
from ...db_drivers.kv_driver import KeyValueDriverConfig
from ...utils.cache_kv.CacheOperations import CacheOperations
from ...utils.agent_stat_analyzer import AgentStatAnalyzerConfig
from ...utils.agent_stat_analyzer.AgentStatOperations import AgentStatOperations


@dataclass
class MemPipelineConfig(BaseComponentConfig, LanguageConfig):
    """Конфигурация Memorize-конвейера.

    :param extractor_config: Конфигурация первой стадии Memorize-конвейера: извлечение информации из текстовых данных и приведение их в triplet-формат. Значение по умолчанию LLMExtractorConfig().
    :type extractor_config: LLMExtractorConfig, optional
    :param updator_config: Конфигурация второй стадии Memorize-конвейера: актуализация знаний в памяти ассистента. Значение по умолчанию LLMUpdatorConfig().
    :type updator_config: LLMUpdatorConfig, optional
    :param log: Отладочный класс для журналирования/мониторинга поведения инициализируемой комопненты. Значение по умолчанию Logger(MEMORIZE_MAIN_LOG_PATH).
    :type log: Logger, optional
    """
    extractor_config: LLMExtractorConfig = field(
        default_factory=lambda: LLMExtractorConfig())
    updator_config: LLMUpdatorConfig = field(
        default_factory=lambda: LLMUpdatorConfig())

    log: Logger = field(default_factory=lambda: Logger(MEMORIZE_MAIN_LOG_PATH))


class MemPipeline(CacheOperations, AgentStatOperations):
    """Верхнеуровневый класс Memorize-конвейера, отвечающий за изменение знаний в памяти ассистента.

    :param kg_model: Модель памяти (графа знаний) ассистента.
    :type kg_model: KnowledgeGraphModel
    :param config: Конфигурация Memorize-конвейера. Значение по умолчанию MemPipelineConfig().
    :type config: MemPipelineConfig, optional
    :param cache_kvdriver_config: Конфигурация структуры данных для кеширования промежуточных результатов в рамках компонент данного класса. Значение по умолчению None.
    :type cache_kvdriver_config: Union[KeyValueDriverConfig, None], optional
    :param inferencestat_config: Конфигурация компоненты для сбора информации и расчёта статистик по результатам выполнения inference-операциий в рамках LLM-задач. Значение по умолчанию None.
    :type inferencestat_config: Union[None, AgentStatAnalyzerConfig], optional
    """

    def __init__(self, kg_model: KnowledgeGraphModel, config: MemPipelineConfig = MemPipelineConfig(),
                 cache_kvdriver_config: Union[None, KeyValueDriverConfig] = None,
                 inferencestat_config: Union[None, AgentStatAnalyzerConfig] = None) -> None:
        self.config = config

        self.stages: MemPipelineStages = MemPipelineStages(
            extractor=LLMExtractor(
                kg_model.AVAILABLE_AGENTS[kg_model.AGENTS_MAP.mem_pipeline],
                config.extractor_config, cache_kvdriver_config, inferencestat_config),
            updator=LLMUpdator(
                kg_model, config.updator_config, cache_kvdriver_config, inferencestat_config)
        )

        self.log = self.config.log
        self.verbose = self.config.verbose

    def remember(self, text: str, time: Union[None, str] = None, properties: Union[None, Dict] = None) -> Tuple[List[Triplet], ReturnInfo]:
        """Метод предназначен для извлечения информации (в виде триплетов) из слабоструктурированного текста и обновление/актуализацию знаний в памяти (графе знаний) ассистента.

        :param text: Слабоструктурированный текст на естественном языке.
        :type text: str
        :param delete_obsolete_info: Если True, то перед добавлением заданной информации будет удалена устаревшая информация из памяти (графа знаний) ассистента, инчае False. Значение по умолчанию False.
        :type delete_obsolete_info: bool, optional
        :param time: Время, с которым ассоциированы события текста.
        :type time: str, optional
        :param properties: Набор свойств, который должен быть сохранён в памяти вмести с извлечённой из текста информацией, Значение по умолчанию dict().
        :type properties: Dict, optional
        :return: Кортеж из двух объектов: (1) список с извлечённой из текста информацией (в виде триплетов), который использовался для обновления/актуализации памяти ассистента; (2) статус завершения операции с пояснительной информацией.
        :rtype: Tuple[List[Triplet], ReturnInfo]
        """

        self.log("START KNOWLEDGE REMEMBERING...", verbose=self.config.verbose)
        self.log(f"BASE_TEXT ID: {create_id(text)}",
                 verbose=self.config.verbose)

        self.log("STAGE#1 - 'Извлечение информации (в структурированном формате) из текста'",
                 verbose=self.config.verbose)
        new_triplets, info = self.stages.extractor.extract_knowledge(
            text, time, properties)

        self.log(f"RESULT: {len(new_triplets)}", verbose=self.config.verbose)
        for triplet in new_triplets:
            self.log(f"* {triplet}", verbose=self.config.verbose)

        if info.status == ReturnStatus.success:
            self.log("STAGE#2 - 'Обновление информации в памяти (графе знаний) асситента'",
                     verbose=self.config.verbose)
            self.log(
                f"TRIPLETS_ID: {create_id(f'{new_triplets}')}", verbose=self.config.verbose)
            info = self.stages.updator.update_knowledge(new_triplets)

        self.log(
            f"STATUS: {STATUS_MESSAGE[info.status]}", verbose=self.config.verbose)

        return new_triplets, info

    def __del__(self):
        # print("deleting Mem-class")
        del self.stages.extractor
        del self.stages.updator
