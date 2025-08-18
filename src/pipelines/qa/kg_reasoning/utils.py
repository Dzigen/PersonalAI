from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Tuple, List

from ....utils import ReturnInfo

@dataclass
class QueryReasoningInfo:
    sub_queries: List[str]
    sub_answers: List[str]

class AbstractKGReasoner(ABC):

    @abstractmethod
    def perform(self, query: str) -> Tuple[str, ReturnInfo]:
        """Метод предназначен для генерации ответа на user-вопрос. Ответ обуславливается на информацию из имеющегося графа знаний.

        :param query: User-вопрос на естественном языке.
        :type query: str
        :return: Кортеж из двух объектов: (1) cгенерированный ответ; (2) статус завершения операции с пояснительной информацией.
        :rtype: Tuple[str, ReturnInfo]
        """
        pass

@dataclass
class BaseKGReasonerConfig:
    pass
