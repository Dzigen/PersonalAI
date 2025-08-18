from dataclasses import dataclass, field
from typing import Tuple, List

from .config import QD_MAIN_LOG_PATH
from ..QueryPreprocessor import QueryPreprocessingInfo
from .....utils.cache_kv import CacheUtils
from .....utils.errors import STATUS_MESSAGE
from .....utils.data_structs import create_id
from .....agents import AgentDriverConfig, AgentDriver
from .....utils import ReturnInfo, Logger, ReturnStatus, AgentTaskSolverConfig, AgentTaskSolver
from .....db_drivers.kv_driver import KeyValueDriverConfig

# TODO

@dataclass
class QueryDenoiserConfig:
    """Конфигурация QueryDenoiser-операции.

    :param lang: Язык, который будет использоваться в подаваемом на вход тексте. На основании выбранного языка будут использоваться соответствующие промпты при инференсе LLM-агента. Если 'auto', то язык определяется автоматически. Значение по умолчанию 'auto'.
    :type lang: str
    :param adriver_config: Конфигурация LLM-агента, который будет использоваться в рамках данной операции. Значение по умолчанию AgentDriverConfig().
    :type adriver_config: AgentDriverConfig

    :param cache_table_name: Название таблицы в структуре (базе) данных, куда будут сохраняться (кешироваться) основные результаты работы QueryDenoiser-класса.
    :type cache_table_name: str
    :param log: Отладочный класс для журналирования/мониторинга поведения инициализируемой компоненты. Значение по умолчанию Logger(QD_MAIN_LOG_PATH).
    :type log: Logger
    :param verbose: Если True, то информация о поведении класса будет сохраняться в stdout и файл-журналирования (log), иначе только в файл. Значение по умолчанию False.
    :type verbose: bool
    """
    lang: str = "auto"
    adriver_config: AgentDriverConfig = field(default_factory=lambda: AgentDriverConfig())

    cache_table_name: str = 'qp_denoising_stage_cache'
    log: Logger = field(default_factory=lambda: Logger(QD_MAIN_LOG_PATH))
    verbose: bool = False

    def to_str(self):
        # TODO
        raise NotImplementedError

class QueryDenoiser(CacheUtils):
    """Класс, реализующий одну из операций по форматированию/предобработке user-вопроса в рамках QueryPreprocessor-стадии. Данный класс выполняет удаление лишних шумов/фрагментов информации из user-вопроса.

    :param config: Конфигурация QueryDenoiser-операции. Значение по умолчанию QueryDenoiserConfig().
    :type config: QueryDenoiserConfig, optional
    :param cache_kvdriver_config:Конфигурация структуры данных для кеширования промежуточных результатов в рамках компонент данного класса. Значение по умолчению None.
    :type cache_kvdriver_config: KeyValueDriverConfig, optional
    :param cache_llm_inference: Если True, то все результаты решения атомарных LLM-задач будут кешировать, иначе False. Значение по умолчанию True.
    :type cache_llm_inference: bool, optional
    """
    def __init__(self, config: QueryDenoiserConfig = QueryDenoiserConfig(),
                 cache_kvdriver_config: KeyValueDriverConfig = None, cache_llm_inference: bool = True):
        self.config = config
        self.cachekv = self.init_cachekv(cache_kvdriver_config, config.cache_table_name)

        self.agent = AgentDriver.connect(config.adriver_config)
        agents_cache_config = None
        if cache_llm_inference:
            agents_cache_config = cache_kvdriver_config if cache_llm_inference else None

        raise NotImplementedError

        self.log = self.config.log
        self.verbose = self.config.verbose

    def get_cache_key(self, query_info: QueryPreprocessingInfo) -> List[object]:
        return [query_info.to_str(), self.config.to_str()]

    @CacheUtils.cache_method_output
    def perform(self, query_info: QueryPreprocessingInfo) -> Tuple[str, ReturnInfo]:
        """Метод предназначен для выполнения операции форматирования/предобработки user-вопроса: декомпозиции сложных/составных user-вопросов на независимые/простые под-вопросы.

        :param query_info: Струкутра данных с результатами предыдущих операций предобратки/форматирования исходного user-вопроса.
        :type query_info: QueryPreprocessingInfo
        :return: Кортеж из двух объектов: (1) модифицированный user-вопрос без информации, зашумляющий основной запрос/интент; (2) статус завершения операции с пояснительной информацией.
        :rtype: Tuple[str, ReturnInfo]
        """
        raise NotImplementedError
