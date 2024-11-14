from abc import abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List

@dataclass
class AgentConnectorConfig:
    #: TODO
    gen_strategy: Dict
    #: TODO
    credentials: Dict = field(default_factory=lambda: dict())
    #: TODO
    ext_params: Dict = field(default_factory=lambda: dict())

class AbstractAgentConnector:
    @abstractmethod
    def check_connection(self) -> bool:
        """_summary_

        :return: _description_
        :rtype: bool
        """
        pass

    @abstractmethod
    def generate(self, system_prompt: str, user_prompt: str, assistant_prompt: str = None) -> str:
        """_summary_

        :param system_prompt: _description_
        :type system_prompt: str
        :param user_prompt: _description_
        :type user_prompt: str
        :param assistant_prompt: _description_, defaults to None
        :type assistant_prompt: str, optional
        :return: _description_
        :rtype: str
        """
        pass
