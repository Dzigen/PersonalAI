from dataclasses import dataclass, field
from typing import Tuple, List, Union, Dict
from copy import deepcopy

from .weak_reasoner import WeakKGReasonerConfig
from .medium_reasoner import MediumKGReasonerConfig
from .config import KGR_MAIN_LOG_PATH, AVAILABLE_KG_REASONERS, AVAILABLE_KGR_CONFIGS
from .utils import BaseKGReasonerConfig, AbstractKGReasoner, KGReasonserStages
from ....utils import ReturnInfo, Logger, CompositeModuleResult
from ....kg_model import KnowledgeGraphModel
from ....db_drivers.kv_driver import KeyValueDriverConfig
from ....utils.cache_kv import CacheUtils
from ....utils.cache_kv.CacheOperations import CacheOperations
from ....utils.agent_stat_analyzer.AgentStatOperations import AgentStatOperations
from ....utils.agent_stat_analyzer import AgentStatAnalyzerConfig
from ....utils.data_structs import BaseComponentConfig, LanguageConfig


@dataclass
class KnowledgeGraphReasonerConfig(BaseComponentConfig, LanguageConfig):
    """
    Конфигурация KnowledgeGraphReasoner-стадии.

    :param reasoner_name: Название версии алгоритма по обходу/ризонинга графа знаний. Значение по умолчанию 'weak'.
    :type reasoner_name: str, optional
    :param reasoner_config: Конфигурация определённой версии обхода/ризонинга графа знаний по извлечению релевантной информации к user-вопросу. Значение по умолчанию WeakKGReasonerConfig().
    :type reasoner_config: Union[Dict,BaseKGReasonerConfig], optional
    """
    reasoner_name: str = 'weak'  # 'weak' | 'medium'
    reasoner_config: Union[Dict, BaseKGReasonerConfig] = field(default_factory=lambda: WeakKGReasonerConfig())  # WeakKGReasonerConfig() | MediumKGReasonerConfig()

    log_path: str = KGR_MAIN_LOG_PATH

    def to_str(self):
        return f"{self.reasoner_name}|{self.reasoner_config.to_str()}"

    @staticmethod
    def from_dict(dict_config: Dict):
        dictconfig_copy = deepcopy(dict_config)
        formated_config = KnowledgeGraphReasonerConfig(**dictconfig_copy)
        formated_config.formate_fields()
        return formated_config

    def formate_fields(self):
        if isinstance(self.reasoner_config, dict):
            self.reasoner_config = AVAILABLE_KGR_CONFIGS[self.reasoner_name].from_dict(self.reasoner_config)


class KnowledgeGraphReasoner(CacheUtils, AbstractKGReasoner, CacheOperations, AgentStatOperations):
    """Верхнеуровневый класс KnowledgeGraphReasoner-стадии (точка входа), отвечающей за поиск информации в графе знаний, релевантной для генерации ответа (на её основе) к user-вопросу.

    :param kg_model: Модель памяти (графа знаний) ассистента.
    :type kg_model: KnowledgeGraphModel
    :param config: Конфигурация KnowledgeGraphReasoner-стадии. Значение по умолчанию KnowledgeGraphReasonerConfig().
    :type config: Union[Dict,KnowledgeGraphReasonerConfig], optional
    :param cache_kvdriver_config: Конфигурация структуры данных для кеширования промежуточных результатов в рамках компонент данного класса. Значение по умолчанию None.
    :type cache_kvdriver_config: Union[KeyValueDriverConfig, None], optional
    :param inferencestat_config: Конфигурация компоненты для сбора информации и расчёта статистик по результатам выполнения inference-операций в рамках LLM-задач. Значение по умолчанию None.
    :type inferencestat_config: Union[None, AgentStatAnalyzerConfig], optional
    """

    def __init__(self, kg_model: KnowledgeGraphModel,
                 config: Union[Dict, KnowledgeGraphReasonerConfig] = KnowledgeGraphReasonerConfig(),
                 cache_kvdriver_config: Union[None, KeyValueDriverConfig] = None,
                 inferencestat_config: Union[None, AgentStatAnalyzerConfig] = None):
        if isinstance(config, dict):
            config: KnowledgeGraphReasonerConfig = KnowledgeGraphReasonerConfig.from_dict(config)
        else:
            config.formate_fields()
        self.config = config

        self.reasoner_name = config.reasoner_name
        self.stages: KGReasonserStages = KGReasonserStages(
            reasoner=AVAILABLE_KG_REASONERS[self.reasoner_name](
                kg_model, config.reasoner_config, cache_kvdriver_config, inferencestat_config
            )
        )

        self.log = Logger(config.log_path)
        self.verbose = config.verbose
        self.log_level = config.log_level

    def get_cache_key(self, query: str) -> List[str]:
        """Формирует ключ кеша для результата работы стадии обхода графа знаний.

        В ключ включается текст исходного запроса, название используемой версии reasoner'а и строковое представление конфигурации KnowledgeGraphReasoner.

        :param query: Исходный user-вопрос.
        :type query: str
        :return: Список строк, используемый как составной ключ кеша.
        :rtype: List[str]
        """
        return [query, self.reasoner_name, self.config.to_str()]

    def perform(self, query: str) -> Tuple[str, ReturnInfo, CompositeModuleResult]:
        """Метод предназначен для генерации ответа на user-вопрос. Ответ обуславливается на информацию из имеющегося графа знаний.

        :param query: User-вопрос на естественном языке.
        :type query: str
        :return: Кортеж из трёх объектов: (1) cгенерированный ответ; (2) статус завершения операции с пояснительной информацией; (3) структура данных с промежуточными результатами реботы метода.
        :rtype: Tuple[str, ReturnInfo, CompositeModuleResult]
        """
        self.log.debug("QUERY: %s", query, verbose=self.verbose, log_level=self.log_level)
        answer, rinfo, trace = self.stages.reasoner.perform(query)
        self.log.debug("RESULT: %s", answer, verbose=self.verbose, log_level=self.log_level)
        self.log.debug("STATUS: %s", rinfo.status, verbose=self.verbose, log_level=self.log_level)
        return answer, rinfo, trace
