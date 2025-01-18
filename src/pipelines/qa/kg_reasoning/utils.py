from abc import ABC, abstractmethod
from dataclasses import dataclass

class AbstractKGReasoner(ABC):

    @abstractmethod
    def perform(self, query: str) -> str:
        pass

@dataclass
class BaseKGReasonerConfig:
    pass
