from dataclasses import dataclass
from enum import Enum
from typing import List, Dict
from abc import ABC, abstractmethod

class AbstractAgentConnector:
    @abstractmethod
    def check_connection(self):
        pass

    @abstractmethod
    def generate(self, user_prompt: str, assistant_prompt: str = None, gen_strategy: Dict = None) -> str:
        pass

class AbstractAgentModel:
    @abstractmethod
    def generate(self, user_prompt: str, assistant_prompt: str = None, gen_strategy: Dict = None) -> str:
        pass

class AgentConnectionType:
    local = 0
    remote = 1

@dataclass
class GeneralAgentConnectionParams:
    pass

@dataclass
class RemoteAgentConnectionParams(GeneralAgentConnectionParams):
    host: str = "localhost"
    gen_path: str = "generate"
    check_path: str = ""
    port: str = "45678"
    
@dataclass
class LocalAgentConnectionParams(GeneralAgentConnectionParams):
    pass