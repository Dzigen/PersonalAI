from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Tuple

from ....utils import ReturnInfo

class AbstractKGReasoner(ABC):

    @abstractmethod
    def perform(self, query: str) -> Tuple[str, ReturnInfo]:
        pass

    @abstractmethod
    def clear_kv_caches(self) -> None:
        pass

@dataclass
class BaseKGReasonerConfig:
    pass
