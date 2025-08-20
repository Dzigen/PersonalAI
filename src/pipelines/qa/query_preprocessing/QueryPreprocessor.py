from dataclasses import dataclass, field
from typing import Tuple, Union, List
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

@dataclass
class QueryPreprocessorConfig:
    """Конфигурация QueryPreprocessor-стадии.

    :param denoising_config: Конфигурация шага предобработки user-вопроса, отвечающая за удаление лишних шумов/фрагментов информации. Если переменная принимает значение None, то данный шаг пропускается. Значение по умолчанию None.
    :type denoising_config: Union[None, QueryDenoiserConfig], optional
    :param enhancing_config: Конфигурация шага предобработки user-вопроса, отвечающая за добавление дополнительных языковых конструкций и переформилирование user-вопроса, с целью упрощения процесса по распознаванию заложенного запроса/интента. Если переменная принимает значение None, то данный шаг пропускается. Значение по умолчанию None.
    :type enhancing_config: Union[None, QueryEnhancerConfig], optional
    :param decomposition_config: Конфигурация шага предобработки user-вопроса, отвечающая за разбиение сложных/составных user-вопрос на простые/независимые части (под-вопросы) для их параллельной обработки и ускорения процесса формирования финального ответа. Если переменная принимает значение None, то данный шаг пропускается. Значение по умолчанию QueryDecomposerConfig().
    :type decomposition_config: Union[None, QueryDecomposerConfig], optional

    :param cache_table_name: Название таблицы в структуре (базе) данных, куда будут сохраняться (кешироваться) основные результаты работы QueryPreprocessor-класса.
    :type cache_table_name: str
    :param log: Отладочный класс для журналирования/мониторинга поведения инициализируемой компоненты. Значение по умолчанию Logger(QP_MAIN_LOG_PATH).
    :type log: Logger
    :param verbose: Если True, то информация о поведении класса будет сохраняться в stdout и файл-журналирования (log), иначе только в файл. Значение по умолчанию False.
    :type verbose: bool
    """
    denoising_config: Union[None, QueryDenoiserConfig] = None
    enhancing_config: Union[None, QueryEnhancerConfig] = None
    decomposition_config: Union[None, QueryDecomposerConfig] = field(default_factory=lambda: QueryDecomposerConfig())

    cache_table_name: str = "query_preprocessing_main_stage_cache"
    log: Logger = field(default_factory=lambda: Logger(QP_MAIN_LOG_PATH))
    verbose: bool = False

    def to_str(self):
        str_denois_config = self.denoising_config.to_str() if self.denoising_config is not None else 'None'
        str_enh_config = self.enhancing_config.to_str() if self.enhancing_config is not None else 'None'
        str_decomp_config = self.decomposition_config.to_str() if self.decomposition_config is not None else 'None'
        return f"{str_denois_config}|{str_enh_config}|{str_decomp_config}"

class QueryPreprocessor(CacheUtils):
    """Верхнеуровневый класс QueryPreprocessor-стадии (точка входа), отвечающей за предобработку исходного user-вопроса, с целью упрощения процесса поиска информации и повышения качества финального ответа системы.

    :param config: Конфигурация QueryPreprocessor-стадии. Значение по умолчанию QueryPreprocessorConfig().
    :type config: QueryPreprocessorConfig, optional
    :param cache_kvdriver_config: Конфигурация структуры данных для кеширования промежуточных результатов в рамках компонент данного класса. Значение по умолчению None.
    :type cache_kvdriver_config: Union[None, KeyValueDriverConfig], optional
    """
    def __init__(self, config: QueryPreprocessorConfig = QueryPreprocessorConfig(),
                 cache_kvdriver_config: Union[None, KeyValueDriverConfig] = None) -> None:
        self.config = config

        self.denoiser = QueryDenoiser(self.config.denoising_config, cache_kvdriver_config) if self.config.denoising_config is not None else None
        self.enhancer = QueryEnhancer(self.config.enhancing_config, cache_kvdriver_config) if self.config.enhancing_config is not None else None
        self.decomposer = QueryDecomposer(self.config.decomposition_config, cache_kvdriver_config) if self.config.decomposition_config is not None else None

        self.cachekv = self.init_cachekv(cache_kvdriver_config, config.cache_table_name)

        self.log = config.log
        self.verbose = config.verbose

    def clear_kv_caches(self, level: str = 'all') -> None:
        if type(level) is not str:
            raise TypeError(f"Аргумент переменной 'level' должен иметь тип 'str'; сейчас аргумент имеет тип '{type(level)}'")
        if level not in ['all', 'current', 'other']:
            raise ValueError(f"Аргумент переменной 'level' должен принимать одно из трёх значенией: 'all', 'current' или 'other'. Полученное значение: '{level}'")

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
        return [query, self.config.to_str()]

    @CacheUtils.cache_method_output
    def perform(self, query: str) -> Tuple[QueryPreprocessingInfo, ReturnInfo]:
        """Метод предназначен для предобработки (удаления шумов, повышения полноты, декомпозии) исходного user-вопроса.

        :param query: User-вопрос на естественном языке.
        :type query: str
        :return: Кортеж из двух объектов: (1) Струкутра данных с предобработанным user-вопросом и результами промежуточных операций; (2) статус завершения операции с пояснительной информацией.
        :rtype: Tuple[QueryPreprocessingInfo, ReturnInfo]
        """
        self.log("START QUERY PREPROCESSING...", verbose=self.config.verbose)
        self.log(f"BASE_QUESTION ID: {create_id(query)}", verbose=self.config.verbose)
        self.log(f"BASE_QUESTION: {query}", verbose=self.config.verbose)
        query_info = QueryPreprocessingInfo(base_query=query)
        rinfo = ReturnInfo()

        if self.denoiser is not None:
           self.log("Удаление шума из запроса...", verbose=self.verbose)
           query_info.denoised_query, den_rinfo = self.denoiser.perform(query_info)
           self.log(f"RESULT: {query_info.denoised_query}", verbose=self.verbose)
           update_rinfo(rinfo, den_rinfo)

        if rinfo.status == ReturnStatus.success and self.enhancer is not None:
           self.log("Корректировка формата запроса...", verbose=self.verbose)
           query_info.enchanced_query, enh_rinfo = self.enhancer.perform(query_info)
           self.log(f"RESULT: {query_info.enchanced_query}", verbose=self.verbose)
           update_rinfo(rinfo, enh_rinfo)

        if rinfo.status == ReturnStatus.success and self.decomposer is not None:
            self.log("Разбиение запроса на независимые части (простые запросы)...", verbose=self.verbose)
            query_info.decomposed_query, dec_rinfo = self.decomposer.perform(query_info)
            self.log(f"RESULT: {query_info.decomposed_query}", verbose=self.verbose)
            update_rinfo(rinfo, dec_rinfo)

        self.log(f"STATUS: {rinfo.status}", verbose=self.verbose)

        if query_info.decomposed_query is not None:
            query_info.processed_query = copy(query_info.decomposed_query)
        elif query_info.enchanced_query is not None:
            query_info.processed_query = [copy(query_info.enchanced_query)]
        elif query_info.denoised_query is not None:
            query_info.processed_query = [copy(query_info.denoised_query)]
        elif query_info.base_query is not None:
            query_info.processed_query = query_info.base_query
        else:
            raise ValueError

        return query_info, rinfo
