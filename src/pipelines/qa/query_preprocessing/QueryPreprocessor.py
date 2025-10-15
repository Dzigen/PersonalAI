from dataclasses import dataclass, field
from typing import Tuple, Union, List, Dict
from copy import copy

from .utils import QueryPreprocessingInfo
from .config import QP_MAIN_LOG_PATH
from .decomposition import QueryDecomposer, QueryDecomposerConfig
from .denoising import QueryDenoiser, QueryDenoiserConfig
from .enhancing import QueryEnhancer, QueryEnhancerConfig
from ....utils import ReturnInfo, Logger, ReturnStatus, update_rinfo
from ....utils.data_structs import create_id
from ....db_drivers.kv_driver import KeyValueDriverConfig
from ....utils.cache_kv import CacheUtils
from ....agents.utils import AbstractAgentConnector
from ....utils.cache_kv.utils import AbstractCacheInfo
from ....utils.agent_stat_analyzer import AgentStatAnalyzerConfig


@dataclass
class QueryPreprocessorConfig:
    """Конфигурация QueryPreprocessor-стадии.

    :param denoising_config: Конфигурация шага предобработки user-вопроса, отвечающая за удаление лишних шумов/фрагментов информации. Если переменная принимает значение None, то данный шаг пропускается. Значение по умолчанию QueryDenoiserConfig().
    :type denoising_config: Union[None, QueryDenoiserConfig], optional
    :param enhancing_config: Конфигурация шага предобработки user-вопроса, отвечающая за добавление дополнительных языковых конструкций и переформилирование user-вопроса, с целью упрощения процесса по распознаванию заложенного запроса/интента. Если переменная принимает значение None, то данный шаг пропускается. Значение по умолчанию QueryEnhancerConfig().
    :type enhancing_config: Union[None, QueryEnhancerConfig], optional
    :param decomposition_config: Конфигурация шага предобработки user-вопроса, отвечающая за разбиение сложных/составных user-вопрос на простые/независимые части (под-вопросы) для их параллельной обработки и ускорения процесса формирования финального ответа. Если переменная принимает значение None, то данный шаг пропускается. Значение по умолчанию QueryDecomposerConfig().
    :type decomposition_config: Union[None, QueryDecomposerConfig], optional
    :param cache_table_name: Название таблицы в структуре (базе) данных, куда будут сохраняться (кешироваться) основные результаты работы QueryPreprocessor-класса. Значение по умолчанию "query_preprocessing_main_stage_cache".
    :type cache_table_name: str, optional
    :param log: Отладочный класс для журналирования/мониторинга поведения инициализируемой компоненты. Значение по умолчанию Logger(QP_MAIN_LOG_PATH).
    :type log: Logger, optional
    :param verbose: Если True, то информация о поведении класса будет сохраняться в stdout и файл-журналирования (log), иначе только в файл. Значение по умолчанию False.
    :type verbose: bool, optional
    """
    denoising_config: Union[None, QueryDenoiserConfig] = field(default_factory=lambda: QueryDenoiserConfig())
    enhancing_config: Union[None, QueryEnhancerConfig] = field(default_factory=lambda: QueryEnhancerConfig())
    decomposition_config: Union[None, QueryDecomposerConfig] = field(default_factory=lambda: QueryDecomposerConfig())

    cache_table_name: str = "query_preprocessing_main_stage_cache"
    log: Logger = field(default_factory=lambda: Logger(QP_MAIN_LOG_PATH))
    verbose: bool = False

    def to_str(self):
        str_denois_config = self.denoising_config.to_str() if self.denoising_config is not None else 'None'
        str_enh_config = self.enhancing_config.to_str() if self.enhancing_config is not None else 'None'
        str_decomp_config = self.decomposition_config.to_str() if self.decomposition_config is not None else 'None'
        return f"{str_denois_config}|{str_enh_config}|{str_decomp_config}"


class QueryPreprocessor(CacheUtils, AbstractCacheInfo):
    """Верхнеуровневый класс QueryPreprocessor-стадии (точка входа), отвечающей за предобработку исходного user-вопроса, с целью упрощения процесса поиска информации и повышения качества финального ответа системы.

    :param agent: Коннектор к конкретному LLM-агенту для выполнения inference-операций.
    :type agent: AbstractAgentConnector
    :param config: Конфигурация QueryPreprocessor-стадии. Значение по умолчанию QueryPreprocessorConfig().
    :type config: QueryPreprocessorConfig, optional
    :param cache_kvdriver_config: Конфигурация структуры данных для кеширования промежуточных результатов в рамках компонент данного класса. Значение по умолчению None.
    :type cache_kvdriver_config: Union[None, KeyValueDriverConfig], optional
    :param inferencestat_config: Конфигурация компоненты для сбора информации и расчёта статистик по результатам выполнения inference-операциий в рамках LLM-задач. Значение по умолчанию None.
    :type inferencestat_config: Union[None, AgentStatAnalyzerConfig], optional
    """

    def __init__(self, agent: AbstractAgentConnector, config: QueryPreprocessorConfig = QueryPreprocessorConfig(),
                 cache_kvdriver_config: Union[None, KeyValueDriverConfig] = None,
                 inferencestat_config: Union[None, AgentStatAnalyzerConfig] = None) -> None:
        self.config = config
        self.using_agent_info = {'kw': agent.CONNECTOR_KW, 'config': agent.config}

        if self.config.denoising_config is not None:
            self.denoiser = QueryDenoiser(
                agent, self.config.denoising_config,
                cache_kvdriver_config,
                inferencestat_config=inferencestat_config)
        else:
            self.denoiser = None

        if self.config.enhancing_config:
            self.enhancer = QueryEnhancer(
                agent, self.config.enhancing_config,
                cache_kvdriver_config,
                inferencestat_config=inferencestat_config)
        else:
            self.enhancer = None

        if self.config.decomposition_config:
            self.decomposer = QueryDecomposer(
                agent, self.config.decomposition_config,
                cache_kvdriver_config,
                inferencestat_config=inferencestat_config)
        else:
            self.decomposer = None

        self.cachekv = self.init_cachekv(
            cache_kvdriver_config, config.cache_table_name)

        self.log = config.log
        self.verbose = config.verbose

    def get_agent_tgen_stat(self) -> Union[None, Dict[str, Union[None, Dict]]]:
        return {
            'denoiser': None if self.denoiser is None else self.denoiser.get_agent_tgen_stat(),
            'enhancer': None if self.enhancer is None else self.enhancer.get_agent_tgen_stat(),
            'decomposer': None if self.decomposer is None else self.decomposer.get_agent_tgen_stat(),
        }

    def get_cache_stat(self) -> Dict[str, Union[None, Dict]]:
        return {
            'QueryPreprocessor': None if self.cachekv is None else self.cachekv.kv_conn.count_items(),
            'denoiser': None if self.denoiser is None else self.denoiser.get_cache_stat(),
            'enhancer': None if self.enhancer is None else self.enhancer.get_cache_stat(),
            'decomposer': None if self.decomposer is None else self.decomposer.get_cache_stat(),
        }

    def clear_kv_caches(self, level: str = 'all') -> None:
        if not isinstance(level, str):
            raise TypeError(
                f"Аргумент переменной 'level' должен иметь тип 'str'; сейчас аргумент имеет тип '{type(level)}'")
        if level not in ['all', 'current', 'other']:
            raise ValueError(
                f"Аргумент переменной 'level' должен принимать одно из трёх значенией: 'all', 'current' или 'other'. Полученное значение: '{level}'")

        if level in ['current', 'all']:
            self.cachekv.clear()

        if level in ['other', 'all']:
            if self.denoiser is not None:
                self.denoiser.clear_kv_caches(level='all')
            if self.enhancer is not None:
                self.enhancer.clear_kv_caches(level='all')
            if self.decomposer is not None:
                self.decomposer.clear_kv_caches(level='all')

    def get_cache_key(self, query: str) -> List[str]:
        str_using_agent_config = f"{self.using_agent_info['kw']}:{self.using_agent_info['config'].to_str()}"
        return [query, self.config.to_str(), str_using_agent_config]

    @CacheUtils.cache_method_output
    def perform(self, query: str) -> Tuple[QueryPreprocessingInfo, ReturnInfo]:
        """Метод предназначен для предобработки (удаления шумов, повышения полноты, декомпозии) исходного user-вопроса.

        :param query: User-вопрос на естественном языке.
        :type query: str
        :return: Кортеж из двух объектов: (1) Струкутра данных с предобработанным user-вопросом и результами промежуточных операций; (2) статус завершения операции с пояснительной информацией.
        :rtype: Tuple[QueryPreprocessingInfo, ReturnInfo]
        """
        self.log("START QUERY PREPROCESSING...", verbose=self.config.verbose)
        self.log(
            f"BASE_QUESTION ID: {create_id(query)}", verbose=self.config.verbose)
        self.log(f"BASE_QUESTION: {query}", verbose=self.config.verbose)
        query_info = QueryPreprocessingInfo(base_query=query)
        rinfo = ReturnInfo()

        if self.denoiser is not None:
            self.log("Удаление шума из запроса...", verbose=self.verbose)
            query_info.denoised_query, den_rinfo = self.denoiser.perform(
                query_info)
            self.log(f"RESULT: {query_info.denoised_query}",
                     verbose=self.verbose)
            update_rinfo(rinfo, den_rinfo)

        if rinfo.status == ReturnStatus.success and self.enhancer is not None:
            self.log("Корректировка формата запроса...", verbose=self.verbose)
            query_info.enchanced_query, enh_rinfo = self.enhancer.perform(
                query_info)
            self.log(f"RESULT: {query_info.enchanced_query}",
                     verbose=self.verbose)
            update_rinfo(rinfo, enh_rinfo)

        if rinfo.status == ReturnStatus.success and self.decomposer is not None:
            self.log(
                "Разбиение запроса на независимые части (простые запросы)...", verbose=self.verbose)
            query_info.decomposed_query, dec_rinfo = self.decomposer.perform(
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
