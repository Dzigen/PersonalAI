from .utils import AbstractAgentConnector, RemoteAgentRequestBody
from .agent_model import AgentModel, AgentModelConfig

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Union
import gc
import requests

class AgentConnectionType:
    local = 0
    remote = 1

@dataclass
class GeneralAgentConnectionParams:
    pass

@dataclass
class RemoteAgentConnectionParams(GeneralAgentConnectionParams):
    host: str
    port: str
    path: str

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
    
    def check_connection(self):
        response = requests.head()
        return response.status_code == 200

    def generate(self, user_prompt: str, assistant_prompt: str = None, gen_strategy: Dict = None) -> str:
        conn_params = self.config.connection_params
        url = f"{conn_params.host}:{conn_params.port}/{conn_params.path}"
        body = {"user_prompt": user_prompt, "assistant_prompt": assistant_prompt, 
                "gen_strategy": gen_strategy}
        response = requests.post(url, json=body)

        if response.status_code == 200:
            output = response.json()['generated_output']
        else:
            raise ValueError

        return output

class LocalAgentConnector(AbstractAgentConnector):
    def __init__(self, config: AgentConnectorConfig) -> None:
        self.config = config
        self.agent = AgentModel(config.agent_config)

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