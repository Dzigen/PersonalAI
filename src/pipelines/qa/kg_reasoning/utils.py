from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Tuple, List

from ....utils import ReturnInfo
from ....utils.cache_kv.utils import AbstractCacheInfo


@dataclass
class QueryReasoningInfo:
    sub_queries: List[str]
    sub_answers: List[str]

    def to_str(self) -> str:
        str_sq = '|'.join(self.sub_queries)
        str_sa = '|'.join(self.sub_answers)
        return f"{str_sq};{str_sa}"


class AbstractKGReasoner(AbstractCacheInfo):

    @abstractmethod
    def perform(self, query: str) -> Tuple[str, ReturnInfo]:
        """Метод предназначен для выполнения ризонинга на графе знаний с помощью указанного запроса с целью извлечения релевантной информации.

        :param query: запрос на естественном языке.
        :type query: str
        :return: Кортеж из двух объектов: (1) извлечённая/релевантная информация/ответа на запрос; (2) статус завершения операции с пояснительной информацией.
        :rtype: Tuple[str, ReturnInfo]
        """
        pass


@dataclass
class BaseKGReasonerConfig:
    pass
