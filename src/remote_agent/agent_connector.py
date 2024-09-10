from .utils import AbstractAgentConnector
from .agent_model import AgentModel, AgentModelConfig

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Union
import gc


class AgentConnectionType:
    local = 0
    remote = 1

@dataclass
class GeneralAgentConnectionParams:
    pass

@dataclass
class RemoteAgentConnectionParams(GeneralAgentConnectionParams):
    url: str
    port: str

@dataclass
class LocalAgentConnectionParams(GeneralAgentConnectionParams):
    pass

@dataclass
class AgentConnectorConfig:
    connection_type: AgentConnectionType = AgentConnectionType.remote
    connection_params: GeneralAgentConnectionParams = field(default_factory=lambda: RemoteAgentConnectionParams())
    agent_config: AgentModelConfig = field(default_factory=lambda: AgentModelConfig())

class RemoteAgentConnector(AbstractAgentConnector):
    def __init__(self, config: AgentConnectorConfig) -> None:
        self.config = config
    
    def open_connection(self):
        pass

    def close_connection(self):
        pass
    def check_connection(self):
        pass

    def generate(self):
        pass

class LocalAgentConnector(AbstractAgentConnector):
    def __init__(self, config: AgentConnectorConfig) -> None:
        self.config = config
        self.open_connection()
        
    def open_connection(self):
        self.agent = AgentModel(self.config.agent_config)

    def close_connection(self):
        del self.agent 
        gc.collect()

    def check_connection(self):
        return hasattr(self, 'agent') and isinstance(self.agent, AbstractAgentConnector)

    def generate(self, user_prompt: str, assistant_prompt: str = None, gen_strategy: Dict = None):
        return self.agent.generate(user_prompt, assistant_prompt, gen_strategy)   

CONNECTORS = {
    AgentConnectionType.local: LocalAgentConnector,
    AgentConnectionType.remote: RemoteAgentConnector
}

class AgentConnector:
    @staticmethod
    def open_connection(config: AgentConnectorConfig):
        return CONNECTORS[config.connection_type](config)