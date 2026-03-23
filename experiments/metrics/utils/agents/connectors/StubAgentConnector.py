from collections import deque
from typing import List, Union, Dict, Tuple

from .configs import DEFAULT_STUBAGENT_CONFIG
from ..utils import AbstractAgentConnector, AgentConnectorConfig, LLMInferenceStat


class StubAgentConnector(AbstractAgentConnector):
    def __init__(self, config: Union[Dict, AgentConnectorConfig] = DEFAULT_STUBAGENT_CONFIG, stub_answers: List[str] = list()) -> None:
        if isinstance(config, dict):
            config = AgentConnectorConfig.from_dict(config)
        else:
            config.formate_fields()
        self.config: AgentConnectorConfig = config

        self.CONNECTOR_KW = 'stub'

        self.looped_answers = deque(stub_answers)

    def check_connection(self) -> bool:
        return True

    def close_connection(self):
        pass

    def generate(self, system_prompt: str, user_prompt: str, assistant_prompt: str = None,
                 gen_strategy: Union[None, Dict[str, str]] = None) -> Tuple[str, LLMInferenceStat]:
        answer = ''
        if len(self.looped_answers):
            answer = self.looped_answers.popleft()
            self.looped_answers.append(answer)

        inference_info = LLMInferenceStat(
            prompt_tokens_amount=0,
            generated_tokens_amount=0,
            inference_elapsed_time=0
        )

        return answer, inference_info

    def __del__(self):
        self.close_connection()
