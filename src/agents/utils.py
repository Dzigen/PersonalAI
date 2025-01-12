from abc import abstractmethod
from dataclasses import dataclass, field
from typing import Dict

@dataclass
class AgentConnectorConfig:
    gen_strategy: Dict = field(default_factory=lambda: dict())
    credentials: Dict = field(default_factory=lambda: dict())
    ext_params: Dict = field(default_factory=lambda: dict())

class AbstractAgentConnector:
    @abstractmethod
    def check_connection(self) -> bool:
        pass

    @abstractmethod
    def generate(self, system_prompt: str, user_prompt: str, assistant_prompt: str = None) -> str:
        pass
