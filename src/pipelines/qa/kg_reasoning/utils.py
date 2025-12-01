from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Tuple, List, Dict

from ...utils import BaseStages
from ....utils import ReturnInfo
from ....utils.cache_kv.CacheOperations import CacheOperations
from ....utils.agent_stat_analyzer.AgentStatOperations import AgentStatOperations
from ....utils.data_structs import BaseConfigOperations


@dataclass
class QueryReasoningInfo:
    """Структура данных для хранения результатов reasoning-стадии.

    :param sub_queries: Список под-запросов, сформированных из исходного пользовательского вопроса.
    :type sub_queries: List[str]
    :param sub_answers: Список ответов/фрагментов информации из графа знаний, соответствующих под-запросам из sub_queries.
    :type sub_answers: List[str]
    """
    sub_queries: List[str]
    sub_answers: List[str]

    def to_str(self) -> str:
        str_sq = '|'.join(self.sub_queries)
        str_sa = '|'.join(self.sub_answers)
        return f"{str_sq};{str_sa}"


class AbstractKGReasoner(CacheOperations, AgentStatOperations):
    """Абстрактный класс алгоритма обхода/ризонинга по графу знаний.

    Определяет интерфейс для конкретных реализаций reasoner'ов (weak/medium).
    """

    @abstractmethod
    def perform(self, query: str) -> Tuple[str, ReturnInfo]:
        """Метод предназначен для выполнения ризонинга на графе знаний с помощью указанного запроса с целью извлечения релевантной информации.

        :param query: запрос на естественном языке.
        :type query: str
        :return: Кортеж из двух объектов: (1) извлечённая/релевантная информация/ответ на запрос; (2) статус завершения операции с пояснительной информацией.
        :rtype: Tuple[str, ReturnInfo]
        """
        pass


@dataclass
class BaseKGReasonerConfig(BaseConfigOperations):
    """Базовый класс конфигураций конкретных алгоритмов обхода/ризонинга по графу знаний."""
    @staticmethod
    def from_dict(dict_config: Dict):
        pass


@dataclass
class KGReasonserStages(BaseStages):
    reasoner: AbstractKGReasoner
