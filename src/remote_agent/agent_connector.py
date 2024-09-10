from .utils import AbstractAgentConnector
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Union

class AgentConnectionType:
    local = 0
    remote = 1

@dataclass
class GeneralAgentConnectionParams:
    gen_strategy: Dict = field(default_factory=lambda: {'early_stoping': True})
    model_name_or_path: str = "Undi95/Meta-Llama-3-8B-Instruct-hf"

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
    params: GeneralAgentConnectionParams = field(default_factory=lambda: RemoteAgentConnectionParams())

class AgentConnector(AbstractAgentConnector):
    
    def open_connection(self):
        pass

    def close_connection(self):
        pass

    def update_gen_strategy(self):
        pass