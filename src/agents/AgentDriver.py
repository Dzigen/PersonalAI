from dataclasses import dataclass, field
from typing import Dict, Union
from copy import deepcopy

from .utils import AgentConnectorConfig, AbstractAgentConnector
from .configs import DEFAULT_AGENT_CONFIGS, AVAILABLE_AGENT_CONNECTORS
from ..utils.data_structs import BaseConfigOperations


@dataclass
class AgentDriverConfig(BaseConfigOperations):
    name: str = 'ollama'
    agent_config: Union[Dict, AgentConnectorConfig] = field(default_factory=lambda: DEFAULT_AGENT_CONFIGS['ollama'])

    def to_str(self):
        self.formate_fields()
        return f"{self.name}|{self.agent_config.to_str()}"

    def formate_fields(self):
        if isinstance(self.agent_config, dict):
            self.agent_config = AgentConnectorConfig.from_dict(self.agent_config)

    @staticmethod
    def from_dict(dict_config: Dict):
        dictconfig_copy = deepcopy(dict_config)
        formated_config = AgentDriverConfig(**dictconfig_copy)
        formated_config.formate_fields()
        return formated_config


class AgentDriver:
    @staticmethod
    def connect(config: Union[Dict, AgentDriverConfig] = AgentDriverConfig()) -> AbstractAgentConnector:
        if isinstance(config, dict):
            config: AgentDriverConfig = AgentDriverConfig.from_dict(config)
        else:
            config.formate_fields()

        return AVAILABLE_AGENT_CONNECTORS[config.name](config.agent_config)
