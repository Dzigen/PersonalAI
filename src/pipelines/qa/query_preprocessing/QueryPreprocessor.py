from dataclasses import dataclass, field
from typing import Tuple, Union, List, Dict
from copy import copy, deepcopy

from .utils import QueryPreprocessingStages
from .config import QP_MAIN_LOG_PATH
from .decomposition import QueryDecomposer, QueryDecomposerConfig
from .denoising import QueryDenoiser, QueryDenoiserConfig
from .enhancing import QueryEnhancer, QueryEnhancerConfig
from ....utils import ReturnInfo, Logger, ReturnStatus, update_rinfo
from ....utils.data_structs import create_id, QueryPreprocessingInfo, BaseComponentConfig, LanguageConfig
from ....db_drivers.kv_driver import KeyValueDriverConfig
from ....utils.cache_kv import CacheUtils
from ....agents.utils import AbstractAgentConnector
from ....utils.cache_kv.CacheOperations import CacheOperations
from ....utils.agent_stat_analyzer.AgentStatOperations import AgentStatOperations
from ....utils.agent_stat_analyzer import AgentStatAnalyzerConfig


@dataclass
class QueryPreprocessorConfig(BaseComponentConfig, LanguageConfig):
    """Конфигурация QueryPreprocessor-стадии.

    :param denoising_config: Конфигурация шага предобработки user-вопроса, отвечающая за удаление лишних шумов/фрагментов информации. Если переменная принимает значение None, то данный шаг пропускается. Значение по умолчанию None.
    :type denoising_config: Union[None, Dict, QueryDenoiserConfig], optional
    :param enhancing_config: Конфигурация шага предобработки user-вопроса, отвечающая за добавление дополнительных языковых конструкций и переформулирование user-вопроса, с целью упрощения процесса по распознаванию заложенного запроса/интента. Если переменная принимает значение None, то данный шаг пропускается. Значение по умолчанию None.
    :type enhancing_config: Union[None, Dict, QueryEnhancerConfig], optional
    :param decomposition_config: Конфигурация шага предобработки user-вопроса, отвечающая за разбиение сложных/составных user-вопрос на простые/независимые части (под-вопросы) для их параллельной обработки и ускорения процесса формирования финального ответа. Если переменная принимает значение None, то данный шаг пропускается. Значение по умолчанию QueryDecomposerConfig().
    :type decomposition_config: Union[None, Dict, QueryDecomposerConfig], optional
    :param cache_table_name: Название таблицы в структуре (базе) данных, куда будут сохраняться (кешироваться) основные результаты работы QueryPreprocessor-класса. Значение по умолчанию "query_preprocessing_main_stage_cache".
    :type cache_table_name: str, optional
    """
    denoising_config: Union[None, Dict, QueryDenoiserConfig] = None
    enhancing_config: Union[None, Dict, QueryEnhancerConfig] = None
    decomposition_config: Union[None, Dict, QueryDecomposerConfig] = field(default_factory=lambda: QueryDecomposerConfig())

    cache_table_name: str = "query_preprocessing_main_stage_cache"
    log: Logger = field(default_factory=lambda: Logger(QP_MAIN_LOG_PATH))

    def to_str(self):
        str_denois_config = self.denoising_config.to_str() if self.denoising_config is not None else 'None'
        str_enh_config = self.enhancing_config.to_str() if self.enhancing_config is not None else 'None'
        str_decomp_config = self.decomposition_config.to_str() if self.decomposition_config is not None else 'None'
        return f"{str_denois_config}|{str_enh_config}|{str_decomp_config}"

    @staticmethod
    def from_dict(dict_config: Dict):
        dictconfig_copy = deepcopy(dict_config)
        formated_dict = QueryPreprocessorConfig(**dictconfig_copy)
        formated_dict.formate_fields()
        return formated_dict

    def formate_fields(self):
        if isinstance(self.denoising_config, dict):
            self.denoising_config = QueryDenoiserConfig.from_dict(self.denoising_config)
        elif self.denoising_config is not None:
            self.denoising_config.formate_fields()

        if isinstance(self.enhancing_config, dict):
            self.enhancing_config = QueryEnhancerConfig.from_dict(self.enhancing_config)
        elif self.enhancing_config is not None:
            self.enhancing_config.formate_fields()

        if isinstance(self.decomposition_config, dict):
            self.decomposition_config = QueryDecomposerConfig.from_dict(self.decomposition_config)
        elif self.decomposition_config is not None:
            self.decomposition_config.formate_fields()


class QueryPreprocessor(CacheUtils, CacheOperations, AgentStatOperations):
    """Верхнеуровневый класс QueryPreprocessor-стадии (точка входа), отвечающей за предобработку исходного user-вопроса, с целью упрощения процесса поиска информации и повышения качества финального ответа системы.

    :param agent: Коннектор к конкретному LLM-агенту для выполнения inference-операций.
    :type agent: AbstractAgentConnector
    :param config: Конфигурация QueryPreprocessor-стадии. Значение по умолчанию QueryPreprocessorConfig().
    :type config: Union[Dict,QueryPreprocessorConfig], optional
    :param cache_kvdriver_config: Конфигурация структуры данных для кеширования промежуточных результатов в рамках компонент данного класса. Значение по умолчанию None.
    :type cache_kvdriver_config: Union[None, KeyValueDriverConfig], optional
    :param inferencestat_config: Конфигурация компоненты для сбора информации и расчёта статистик по результатам выполнения inference-операций в рамках LLM-задач. Значение по умолчанию None.
    :type inferencestat_config: Union[None, AgentStatAnalyzerConfig], optional
    """

    def __init__(self, agent: AbstractAgentConnector, config: Union[Dict, QueryPreprocessorConfig] = QueryPreprocessorConfig(),
                 cache_kvdriver_config: Union[None, KeyValueDriverConfig] = None,
                 inferencestat_config: Union[None, AgentStatAnalyzerConfig] = None) -> None:
        if isinstance(config, dict):
            config: QueryPreprocessorConfig = QueryPreprocessorConfig.from_dict(config)
        else:
            config.formate_fields()
        self.config = config

        self.using_agent_info = {'kw': agent.CONNECTOR_KW, 'config': agent.config}

        self.stages: QueryPreprocessingStages = QueryPreprocessingStages()

        if self.config.denoising_config is not None:
            self.stages.denoiser = QueryDenoiser(
                agent, self.config.denoising_config, cache_kvdriver_config, inferencestat_config)

        if self.config.enhancing_config is not None:
            self.stages.enhancer = QueryEnhancer(
                agent, self.config.enhancing_config, cache_kvdriver_config, inferencestat_config)

        if self.config.decomposition_config is not None:
            self.stages.decomposer = QueryDecomposer(
                agent, self.config.decomposition_config, cache_kvdriver_config, inferencestat_config)

        self.cachekv = self.init_cachekv(
            cache_kvdriver_config, config.cache_table_name)

        self.log = config.log
        self.verbose = config.verbose

    def get_cache_key(self, query: str) -> List[str]:
        """Метод формирует ключ кеша для результата предобработки вопроса.
        В ключ включаются текст исходного запроса, строковое представление конфигурации и идентификатор используемого LLM-агента.

        :param query: Исходный user-вопрос.
        :type query: str
        :return: Список строк, используемый как составной ключ кеша.
        :rtype: List[str]
        """
        str_using_agent_config = f"{self.using_agent_info['kw']}:{self.using_agent_info['config'].to_str()}"
        return [query, self.config.to_str(), str_using_agent_config]

    @CacheUtils.cache_method_output
    def perform(self, query: str) -> Tuple[QueryPreprocessingInfo, ReturnInfo]:
        """Метод предназначен для предобработки (удаления шумов, повышения полноты, декомпозиции) исходного user-вопроса.

        :param query: User-вопрос на естественном языке.
        :type query: str
        :return: Кортеж из двух объектов: (1) Структура данных с предобработанным user-вопросом и результатами промежуточных операций; (2) статус завершения операции с пояснительной информацией.
        :rtype: Tuple[QueryPreprocessingInfo, ReturnInfo]
        """
        self.log("START QUERY PREPROCESSING...", verbose=self.verbose)
        self.log(
            f"BASE_QUESTION ID: {create_id(query)}", verbose=self.verbose)
        self.log(f"BASE_QUESTION: {query}", verbose=self.verbose)
        query_info = QueryPreprocessingInfo(base_query=query)
        rinfo = ReturnInfo()

        if self.stages.denoiser is not None:
            self.log("Удаление шума из запроса...", verbose=self.verbose)
            query_info.denoised_query, den_rinfo = self.stages.denoiser.perform(
                query_info)
            self.log(f"RESULT: {query_info.denoised_query}",
                     verbose=self.verbose)
            update_rinfo(rinfo, den_rinfo)

        if (rinfo.status == ReturnStatus.success) and (self.stages.enhancer is not None):
            self.log("Корректировка формата запроса...", verbose=self.verbose)
            query_info.enchanced_query, enh_rinfo = self.stages.enhancer.perform(
                query_info)
            self.log(f"RESULT: {query_info.enchanced_query}",
                     verbose=self.verbose)
            update_rinfo(rinfo, enh_rinfo)

        if (rinfo.status == ReturnStatus.success) and (self.stages.decomposer is not None):
            self.log(
                "Разбиение запроса на независимые части (простые запросы)...", verbose=self.verbose)
            query_info.decomposed_query, dec_rinfo = self.stages.decomposer.perform(
                query_info)
            self.log(f"RESULT: {query_info.decomposed_query}",
                     verbose=self.verbose)
            update_rinfo(rinfo, dec_rinfo)

        self.log(f"STATUS: {rinfo.status}", verbose=self.verbose)

        if query_info.decomposed_query is not None:
            query_info.processed_query = copy(query_info.decomposed_query)
        elif query_info.enchanced_query is not None:
            query_info.processed_query = [copy(query_info.enchanced_query)]
        elif query_info.denoised_query is not None:
            query_info.processed_query = [copy(query_info.denoised_query)]
        elif query_info.base_query is not None:
            query_info.processed_query = [copy(query_info.base_query)]
        else:
            raise ValueError

        return query_info, rinfo
