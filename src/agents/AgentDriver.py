from dataclasses import dataclass, field

from .utils import AgentConnectorConfig, AbstractAgentConnector
from .configs import DEFAULT_AGENT_CONFIGS, AVAILABLE_AGENT_CONNECTORS

@dataclass
class AgentDriverConfig:
    name: str = 'gigachat'
    agent_config: AgentConnectorConfig = field(default_factory=lambda: DEFAULT_AGENT_CONFIGS['gigachat'])

class AgentDriver:
    @staticmethod
    def connect(config: AgentDriverConfig = AgentDriverConfig()) -> AbstractAgentConnector:
        """_summary_

        :param config: _description_, defaults to AgentDriverConfig()
        :type config: AgentDriverConfig, optional
        :return: _description_
        :rtype: AbstractAgentConnector
        """
        return AVAILABLE_AGENT_CONNECTORS[config.name](config.agent_config)
