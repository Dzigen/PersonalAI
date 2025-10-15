from dataclasses import dataclass, field
from typing import Tuple, List, Union, Dict

from .weak_reasoner import WeakKGReasonerConfig
from .medium_reasoner import MediumKGReasonerConfig
from .config import KGR_MAIN_LOG_PATH, AVAILABLE_KG_REASONERS
from .utils import BaseKGReasonerConfig, AbstractKGReasoner
from ....utils import ReturnInfo, Logger
from ....kg_model import KnowledgeGraphModel
from ....db_drivers.kv_driver import KeyValueDriverConfig
from ....utils.cache_kv import CacheUtils
from ....utils.cache_kv.utils import AbstractCacheInfo
from ....utils.agent_stat_analyzer import AgentStatAnalyzerConfig


@dataclass
class KnowledgeGraphReasonerConfig:
    """
    Конфигурация KnowledgeGraphReasoner-стадии.

    :param reasoner_name: Название версии алгоритма по обходу/ризонинга графа знаний. Значение по умолчанию 'weak'.
    :type reasoner_name: str, optional
    :param reasoner_hyperparameters: Конфигурация определённой версии обхода/ризонинга графа знаний по извлечению релевантной информации к user-вопросу. Значение по умолчанию WeakKGReasonerConfig().
    :type reasoner_hyperparameters: BaseKGReasonerConfig, optional
    :param cache_table_name: Название таблицы в структуре (базе) данных, куда будут сохраняться (кешироваться) основные результаты работы KnowledgeGraphReasoner-класса. Значение по умолчанию 'kg_reasoning_main_stage_cache'.
    :type cache_table_name: str, optional
    :param log: Отладочный класс для журналирования/мониторинга поведения инициализируемой компоненты. Значение по умолчанию Logger(KGR_MAIN_LOG_PATH).
    :type log: Logger, optional
    :param verbose: Если True, то информация о поведении класса будет сохраняться в stdout и файл-журналирования (log), иначе только в файл. Значение по умолчанию False.
    :type verbose: bool, optional
    """
    reasoner_name: str = 'medium'  # 'weak' | 'medium'
    reasoner_hyperparameters: BaseKGReasonerConfig = field(
        default_factory=lambda: MediumKGReasonerConfig())

    cache_table_name: str = 'kg_reasoning_main_stage_cache'
    log: Logger = field(default_factory=lambda: Logger(KGR_MAIN_LOG_PATH))
    verbose: bool = False

    def to_str(self):
        return f"{self.reasoner_name}|{self.reasoner_hyperparameters.to_str()}"


class KnowledgeGraphReasoner(CacheUtils, AbstractCacheInfo):
    """Верхнеуровневый класс KnowledgeGraphReasoner-стадии (точка входа), отвечающей за поиск информации в графе знаний, релевантной для генерации ответа (на её основе) к user-вопросу.

    :param kg_model: Модель памяти (графа знаний) ассистента.
    :type kg_model: KnowledgeGraphModel
    :param config: Конфигурация KnowledgeGraphReasoner-стадии. Значение по умолчанию KnowledgeGraphReasonerConfig().
    :type config: KnowledgeGraphReasonerConfig, optional
    :param cache_kvdriver_config: Конфигурация структуры данных для кеширования промежуточных результатов в рамках компонент данного класса. Значение по умолчению None.
    :type cache_kvdriver_config: Union[KeyValueDriverConfig, None], optional
    :param inferencestat_config: Конфигурация компоненты для сбора информации и расчёта статистик по результатам выполнения inference-операциий в рамках LLM-задач. Значение по умолчанию None.
    :type inferencestat_config: Union[None, AgentStatAnalyzerConfig], optional
    """

    def __init__(self, kg_model: KnowledgeGraphModel,
                 config: KnowledgeGraphReasonerConfig = KnowledgeGraphReasonerConfig(),
                 cache_kvdriver_config: Union[None, KeyValueDriverConfig] = None,
                 inferencestat_config: Union[None, AgentStatAnalyzerConfig] = None):
        self.config = config

        self.cachekv = self.init_cachekv(
            cache_kvdriver_config, config.cache_table_name)

        self.reasoner_name = config.reasoner_name
        self.reasoner: AbstractKGReasoner = AVAILABLE_KG_REASONERS[self.reasoner_name](
            kg_model, config.reasoner_hyperparameters, cache_kvdriver_config, inferencestat_config)

        self.log = config.log
        self.verbose = config.verbose

    def get_agent_tgen_stat(self) -> Union[None, Dict[str, Union[None, Dict]]]:
        return {
            'reasoner': self.reasoner.get_agent_tgen_stat()
        }

    def get_cache_stat(self) -> Dict[str, Union[None, Dict]]:
        return {
            'KnowledgeGraphReasoner': None if self.cachekv is None else self.cachekv.kv_conn.count_items(),
            'reasoner': self.reasoner.get_cache_stat()
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
            self.reasoner.clear_kv_caches(level='all')

    def get_cache_key(self, query: str) -> List[str]:
        return [query, self.reasoner_name, self.config.to_str()]

    @CacheUtils.cache_method_output
    def perform(self, query: str) -> Tuple[str, ReturnInfo]:
        """Метод предназначен для генерации ответа на user-вопрос. Ответ обуславливается на информацию из имеющегося графа знаний.

        :param query: User-вопрос на естественном языке.
        :type query: str
        :return: Кортеж из двух объектов: (1) cгенерированный ответ; (2) статус завершения операции с пояснительной информацией.
        :rtype: Tuple[str, ReturnInfo]
        """
        answer, info = self.reasoner.perform(query)
        return answer, info
