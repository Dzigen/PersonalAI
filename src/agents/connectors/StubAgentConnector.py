from collections import deque
from typing import List, Union, Dict

from .configs import DEFAULT_STUBAGENT_CONFIG
from ..utils import AbstractAgentConnector, AgentConnectorConfig


class StubAgentConnector(AbstractAgentConnector):
    def __init__(self, config: AgentConnectorConfig = DEFAULT_STUBAGENT_CONFIG, stub_answers: List[str] = list()) -> None:
        self.config = config
        self.looped_answers = deque(stub_answers)
        self.CONNECTOR_KW = 'stub'

    def check_connection(self) -> bool:
        return True

    def close_connection(self):
        pass

    def generate(self, system_prompt: str, user_prompt: str, assistant_prompt: str = None, gen_strategy: Union[None, Dict[str, str]] = None) -> str:
        answer = ''
        if len(self.looped_answers):
            answer = self.looped_answers.popleft()
            self.looped_answers.append(answer)
        return answer

    def __del__(self):
        self.close_connection()
