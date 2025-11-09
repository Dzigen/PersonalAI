from dataclasses import dataclass, field
from typing import Tuple, List, Union, Dict
from copy import deepcopy

from .weak_reasoner import WeakKGReasonerConfig
from .medium_reasoner import MediumKGReasonerConfig
from .config import KGR_MAIN_LOG_PATH, AVAILABLE_KG_REASONERS, AVAILABLE_KGR_CONFIGS
from .utils import BaseKGReasonerConfig, AbstractKGReasoner, KGReasonserStages
from ....utils import ReturnInfo, Logger
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
    :param cache_table_name: Название таблицы в структуре (базе) данных, куда будут сохраняться (кешироваться) основные результаты работы KnowledgeGraphReasoner-класса. Значение по умолчанию 'kg_reasoning_main_stage_cache'.
    :type cache_table_name: str, optional
    """
    reasoner_name: str = 'weak'  # 'weak' | 'medium'
    reasoner_config: Union[Dict, BaseKGReasonerConfig] = field(default_factory=lambda: WeakKGReasonerConfig())  # WeakKGReasonerConfig() | MediumKGReasonerConfig()

    cache_table_name: str = 'kg_reasoning_main_stage_cache'
    log: Logger = field(default_factory=lambda: Logger(KGR_MAIN_LOG_PATH))

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
    :param cache_kvdriver_config: Конфигурация структуры данных для кеширования промежуточных результатов в рамках компонент данного класса. Значение по умолчению None.
    :type cache_kvdriver_config: Union[KeyValueDriverConfig, None], optional
    :param inferencestat_config: Конфигурация компоненты для сбора информации и расчёта статистик по результатам выполнения inference-операциий в рамках LLM-задач. Значение по умолчанию None.
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

        self.cachekv = self.init_cachekv(
            cache_kvdriver_config, config.cache_table_name)

        self.reasoner_name = config.reasoner_name
        self.stages: KGReasonserStages = KGReasonserStages(
            reasoner=AVAILABLE_KG_REASONERS[self.reasoner_name](
                kg_model, config.reasoner_config, cache_kvdriver_config, inferencestat_config
            )
        )

        self.log = config.log
        self.verbose = config.verbose

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
        answer, rinfo = self.stages.reasoner.perform(query)
        self.log(f"RESULT: {answer}", verbose=self.verbose)
        self.log(f"STATUS: {rinfo.status}", verbose=self.verbose)
        return answer, rinfo
