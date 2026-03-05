from dataclasses import dataclass, field
from typing import Dict, Union
from copy import deepcopy

from .utils import AgentConnectorConfig, AbstractAgentConnector
from .configs import DEFAULT_AGENT_CONFIGS, AVAILABLE_AGENT_CONNECTORS
from ..data_structs import BaseConfigOperations


@dataclass
class AgentDriverConfig(BaseConfigOperations):
    """Конфигурация драйвера LLM-агента.

    :param name: Ключ коннектора, который будет использован ('ollama', 'local', 'gigachat' и тд).
    :type name: str
    :param agent_config: Конфигурация выбранного коннектора либо словарь с параметрами этой конфигурации.
    :type agent_config: Union[Dict, AgentConnectorConfig]
    """
    name: str = 'ollama'
    agent_config: Union[Dict, AgentConnectorConfig] = field(default_factory=lambda: DEFAULT_AGENT_CONFIGS['ollama'])

    def to_str(self):
        """Формирует строковое представление конфигурации драйвера."""
        self.formate_fields()
        return f"{self.name}|{self.agent_config.to_str()}"

    def formate_fields(self):
        """Приводит поле agent_config к согласованному типу."""
        if isinstance(self.agent_config, dict):
            self.agent_config = AgentConnectorConfig.from_dict(self.agent_config)

    @staticmethod
    def from_dict(dict_config: Dict):
        """Создаёт экземпляр AgentDriverConfig на основе словаря.

        :param dict_config: Словарь с ключами, соответствующими полям конфигурации.
        :type dict_config: Dict
        :return: Нормализованная конфигурация драйвера агента.
        :rtype: AgentDriverConfig
        """
        dictconfig_copy = deepcopy(dict_config)
        formated_config = AgentDriverConfig(**dictconfig_copy)
        formated_config.formate_fields()
        return formated_config


class AgentDriver:
    """Компоненты для инициализации коннектора к LLM-агенту по заданной конфигурации."""
    @staticmethod
    def connect(config: Union[Dict, AgentDriverConfig] = AgentDriverConfig()) -> AbstractAgentConnector:
        """Создаёт и инициализирует коннектор к LLM-агенту по заданной конфигурации.

        :param config: Конфигурация драйвера либо словарь с параметрами.
        :type config: Union[Dict, AgentDriverConfig]
        :return: Инициализированный коннектор, реализующий интерфейс AbstractAgentConnector.
        :rtype: AbstractAgentConnector
        """
        if isinstance(config, dict):
            config: AgentDriverConfig = AgentDriverConfig.from_dict(config)
        else:
            config.formate_fields()

        return AVAILABLE_AGENT_CONNECTORS[config.name](config.agent_config)
