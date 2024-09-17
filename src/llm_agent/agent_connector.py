from .utils import AbstractAgentConnector
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
    host: str = "10.16.88.76"
    gen_path: str = "generate"
    check_path: str = ""
    port: str = "45678"
    
@dataclass
class LocalAgentConnectionParams(GeneralAgentConnectionParams):
    pass

@dataclass
class AgentConnectorConfig:
    connection_type: AgentConnectionType = AgentConnectionType.remote
    connection_params: GeneralAgentConnectionParams = field(default_factory=lambda: RemoteAgentConnectionParams())
    agent_config: AgentModelConfig = field(default_factory=lambda: AgentModelConfig())

class RemoteAgentConnector(AbstractAgentConnector):
    def __init__(self, config: AgentConnectorConfig = AgentConnectorConfig()) -> None:
        self.config = config
    
    def check_connection(self) -> bool:
        """Метод для проверка на наличие запущенного api с llm-агентом, 
        который готов принимать и обробатывать запросы.

        Returns:
            bool: Если True, то api с llm-агентов в работоспособном состоянии, иначе False.
        """
        conn_params = self.config.connection_params
        url = f"http://{conn_params.host}:{conn_params.port}/{conn_params.check_path}"
        response = requests.get(url)
        return response.status_code == 200

    def generate(self, user_prompt: str, assistant_prompt: str = None, system_prompt: str = None, gen_strategy: Dict = None) -> str:
        """Метод для отправки текстовых звапросов llm-агенту для получения сгенерированных ответов.

        Args:
            user_prompt (str): Запрос для llm-агента.
            assistant_prompt (str, optional): Дополнительная к user_prompt-запросу информация, 
                                              которая может быть использована llm-агентом при генерации ответа. Defaults to None.
            gen_strategy (Dict, optional): Стретегия генерации текстовой последовательности для llm-агента. Defaults to None.

        Raises:
            ValueError: От api c llm-агентов пришёл ответ со status_code-значением, отличным от 200.

        Returns:
            str: Текстовая последовательность, сгенерированная llm-агентом.
        """
        conn_params = self.config.connection_params
        url = f"http://{conn_params.host}:{conn_params.port}/{conn_params.gen_path}"
        body = {"user_prompt": user_prompt}
        if assistant_prompt is not None:
            body["assistant_prompt"] = assistant_prompt
        if gen_strategy is not None:
            body["gen_strategy"] = gen_strategy
        if system_prompt is not None:
            body["system_prompt"] = system_prompt
        response = requests.post(url, json=body)

        if response.status_code == 200:
            output = response.json()['generated_output']
        else:
            raise ValueError

        return output

class LocalAgentConnector(AbstractAgentConnector):
    def __init__(self, config: AgentConnectorConfig = AgentConnectorConfig()) -> None:
        self.config = config
        self.agent = AgentModel(config.agent_config)

    def check_connection(self):
        return hasattr(self, 'agent') and isinstance(self.agent, AbstractAgentConnector)

    def generate(self, user_prompt: str, assistant_prompt: str = None, gen_strategy: Dict = None):
        return self.agent.generate(user_prompt, assistant_prompt, gen_strategy)   

# Доступные способы соединения с llm-агентом
CONNECTORS = {
    AgentConnectionType.local: LocalAgentConnector,
    AgentConnectionType.remote: RemoteAgentConnector
}

class AgentConnector:
    @staticmethod
    def open(config: AgentConnectorConfig):
        return CONNECTORS[config.connection_type](config)