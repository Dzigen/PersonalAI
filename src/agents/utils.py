from abc import abstractmethod
from dataclasses import dataclass, field
from copy import deepcopy

from typing import Dict, Union, Tuple
from ..utils.agent_stat_analyzer.utils import LLMInferenceStat
from ..utils.data_structs import BaseConfigOperations


@dataclass
class AgentConnectorConfig(BaseConfigOperations):
    gen_strategy: Dict = field(default_factory=lambda: dict())
    credentials: Dict = field(default_factory=lambda: dict())
    ext_params: Dict = field(default_factory=lambda: dict())

    def to_str(self):
        str_genstrat = ";".join(list(map(lambda p: f"{p[0]}={p[1]}", sorted(
            [(k, str(v)) for k, v in self.gen_strategy.items()], key=lambda p: p[0]))))
        str_creds = ";".join(list(map(lambda p: f"{p[0]}={p[1]}", sorted(
            [(k, str(v)) for k, v in self.credentials.items()], key=lambda p: p[0]))))
        return f"{str_genstrat}|{str_creds}"

    @staticmethod
    def from_dict(dict_config: Dict):
        dictconfig_copy = deepcopy(dict_config)
        formated_config = AgentConnectorConfig(**dictconfig_copy)
        formated_config.formate_fields()
        return formated_config


class AbstractAgentConnector:
    CONNECTOR_KW: Union[None, str] = None
    config: Union[None, AgentConnectorConfig] = None

    @abstractmethod
    def check_connection(self) -> bool:
        pass

    @abstractmethod
    def generate(self, system_prompt: str, user_prompt: str, assistant_prompt: str = None,
                 gen_strategy: Union[None, Dict[str, str]] = None) -> Tuple[str, LLMInferenceStat]:
        pass

    @abstractmethod
    def close_connection(self) -> None:
        pass

    def __del__(self) -> None:
        self.close_connection()
