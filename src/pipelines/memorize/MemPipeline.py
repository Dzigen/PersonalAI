from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Union
from copy import deepcopy

from .configs import MEMORIZE_MAIN_LOG_PATH
from .extractor.LLMExtractor import LLMExtractor
from .updator.LLMUpdator import LLMUpdator
from .extractor import LLMExtractorConfig
from .updator import LLMUpdatorConfig
from .utils import MemPipelineStages
from ...kg_model import KnowledgeGraphModel
from ...utils import Logger, Triplet, ReturnStatus, ReturnInfo, \
    accumulate_stage_info, CompositeModuleDetailedResult, ModuleType
from ...utils.data_structs import create_id, BaseComponentConfig, LanguageConfig
from ...utils.errors import STATUS_MESSAGE, update_rinfo
from ...db_drivers.kv_driver import KeyValueDriverConfig
from ...utils.cache_kv.CacheOperations import CacheOperations
from ...utils.agent_stat_analyzer import AgentStatAnalyzerConfig
from ...utils.agent_stat_analyzer.AgentStatOperations import AgentStatOperations


@dataclass
class MemPipelineConfig(BaseComponentConfig, LanguageConfig):
    """Конфигурация Memorize-конвейера.

    :param extractor_config: Конфигурация первой стадии Memorize-конвейера: извлечение информации из текстовых данных и приведение их в triplet-формат. Значение по умолчанию LLMExtractorConfig().
    :type extractor_config: Union[Dict, LLMExtractorConfig], optional
    :param updator_config: Конфигурация второй стадии Memorize-конвейера: актуализация знаний в памяти ассистента. Значение по умолчанию LLMUpdatorConfig().
    :type updator_config: Union[Dict, LLMUpdatorConfig], optional
    """
    extractor_config: Union[Dict, LLMExtractorConfig] = field(
        default_factory=lambda: LLMExtractorConfig())
    updator_config: Union[Dict, LLMUpdatorConfig] = field(
        default_factory=lambda: LLMUpdatorConfig())

    log: Logger = field(default_factory=lambda: Logger(MEMORIZE_MAIN_LOG_PATH))

    def to_str(self):
        # TODO
        raise NotImplementedError

    @staticmethod
    def from_dict(dict_config: Dict):
        dictconfig_copy = deepcopy(dict_config)
        formated_config = MemPipelineConfig(**dictconfig_copy)
        formated_config.formate_fields()
        return formated_config

    def formate_fields(self):
        if isinstance(self.extractor_config, dict):
            self.extractor_config = LLMExtractorConfig.from_dict(self.extractor_config)
        else:
            self.extractor_config.formate_fields()

        if isinstance(self.updator_config, dict):
            self.updator_config = LLMUpdatorConfig.from_dict(self.updator_config)
        else:
            self.updator_config.formate_fields()


class MemPipeline(CacheOperations, AgentStatOperations):
    """Верхнеуровневый класс Memorize-конвейера, отвечающий за изменение знаний в памяти ассистента.

    :param kg_model: Модель памяти (графа знаний) ассистента.
    :type kg_model: KnowledgeGraphModel
    :param config: Конфигурация Memorize-конвейера. Значение по умолчанию MemPipelineConfig().
    :type config: Union[Dict, MemPipelineConfig], optional
    :param cache_kvdriver_config: Конфигурация структуры данных для кеширования промежуточных результатов в рамках компонент данного класса. Значение по умолчанию None.
    :type cache_kvdriver_config: Union[KeyValueDriverConfig, None], optional
    :param inferencestat_config: Конфигурация компоненты для сбора информации и расчёта статистик по результатам выполнения inference-операций в рамках LLM-задач. Значение по умолчанию None.
    :type inferencestat_config: Union[None, AgentStatAnalyzerConfig], optional
    """

    def __init__(self, kg_model: KnowledgeGraphModel, config: Union[Dict, MemPipelineConfig] = MemPipelineConfig(),
                 cache_kvdriver_config: Union[None, KeyValueDriverConfig] = None,
                 inferencestat_config: Union[None, AgentStatAnalyzerConfig] = None) -> None:
        if isinstance(config, dict):
            config: MemPipelineConfig = MemPipelineConfig.from_dict(config)
        else:
            config.formate_fields()

        self.stages: MemPipelineStages = MemPipelineStages(
            extractor=LLMExtractor(
                kg_model.AVAILABLE_AGENTS[kg_model.AGENTS_MAP.mem_pipeline],
                config.extractor_config, cache_kvdriver_config, inferencestat_config),
            updator=LLMUpdator(
                kg_model, config.updator_config, cache_kvdriver_config, inferencestat_config)
        )

        self.log = config.log
        self.verbose = config.verbose

    @accumulate_stage_info
    def remember(self, text: str, time: Union[None, str] = None, properties: Union[None, Dict] = None) -> Tuple[List[Triplet], ReturnInfo, CompositeModuleDetailedResult]:
        """Метод предназначен для извлечения информации (в виде триплетов) из слабоструктурированного текста и обновление/актуализацию знаний в памяти (графе знаний) ассистента.

        :param text: Слабоструктурированный текст на естественном языке.
        :type text: str
        :param delete_obsolete_info: Если True, то перед добавлением заданной информации будет удалена устаревшая информация из памяти (графа знаний) ассистента, иначе False. Значение по умолчанию False.
        :type delete_obsolete_info: bool, optional
        :param time: Время, с которым ассоциированы события текста.
        :type time: str, optional
        :param properties: Набор свойств, который должен быть сохранён в памяти вместе с извлечённой из текста информацией. Значение по умолчанию None.
        :type properties: Dict, optional
        :return: Кортеж из двух объектов: (1) список с извлечённой из текста информацией (в виде триплетов), который использовался для обновления/актуализации памяти ассистента; (2) статус завершения операции с пояснительной информацией.
        :rtype: Tuple[List[Triplet], ReturnInfo]
        """

        self.log("START KNOWLEDGE REMEMBERING...", verbose=self.verbose)
        self.log(f"BASE_TEXT ID: {create_id(text)}", verbose=self.verbose)
        rinfo, module_trace = ReturnInfo(), CompositeModuleDetailedResult()

        self.log("STAGE#1 - 'Извлечение информации (в структурированном формате) из текста'", verbose=self.verbose)
        new_triplets, extract_rinfo, trace = self.stages.extractor.extract_knowledge(text, time, properties)

        self.log(f"STATUS: {extract_rinfo.status}", verbose=self.verbose)
        module_trace.add('extract_knowledge', ModuleType.stage, trace)
        update_rinfo(rinfo, extract_rinfo)
        self.log(f"RESULT: {len(new_triplets)}", verbose=self.verbose)
        for triplet in new_triplets:
            self.log(f"* {triplet}", verbose=self.verbose)

        if extract_rinfo.status == ReturnStatus.success:
            self.log("STAGE#2 - 'Обновление информации в памяти (графе знаний) ассистента'", verbose=self.verbose)
            self.log(f"TRIPLETS_ID: {create_id(f'{new_triplets}')}", verbose=self.verbose)
            delete_add_info, update_rinfo, trace = self.stages.updator.update_knowledge(new_triplets)

            self.log(f"STATUS: {update_rinfo.status}", verbose=self.verbose)
            module_trace.add('update_knowledge', ModuleType.stage, trace)
            update_rinfo(rinfo, update_rinfo)
            self.log(f"RESULT:", verbose=self.verbose)
            self.log(f"* triplets deletion info: {delete_add_info[0]}", verbose=self.verbose)
            self.log(f"* added triplet info: {delete_add_info[1]}", verbose=self.verbose)

        return new_triplets, rinfo, module_trace

    def close_connections(self):
        self.stages.close_connections()
