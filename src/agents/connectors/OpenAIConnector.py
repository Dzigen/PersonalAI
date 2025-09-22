import os
from openai import OpenAI
from typing import Dict, Union

from .configs import DEEPSEEK_CONFIG, GPT4OMINI_CONFIG
from ..utils import AbstractAgentConnector, AgentConnectorConfig


class OpenAIConnector(AbstractAgentConnector):
    def __init__(self, config: AgentConnectorConfig = DEEPSEEK_CONFIG) -> None:
        self.config = config
        base_url = None if config.credentials['base_url'] == 'None' else config.credentials['base_url']
        self.config.credentials['base_url'] = base_url

        self.client = OpenAI(
            api_key=os.environ.get(
                "OPENAI_API_KEY", config.credentials['token']),
            base_url=config.credentials['base_url'])

    def check_connection(self):
        # TODO
        pass

    def close_connection(self):
        self.client.close()

    def generate(self, system_prompt: str, user_prompt: str, assistant_prompt: str = None, gen_strategy: Union[None, Dict[str, str]] = None) -> str:
        msgs = [{"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}]
        if assistant_prompt is not None:
            msgs.append({"role": "assistant", "content": assistant_prompt})

        gen_strategy = self.config.gen_strategy if gen_strategy is None else gen_strategy
        completion = self.client.chat.completions.create(
            model=self.config.credentials['model'],
            messages=msgs, **gen_strategy)

        return completion.choices[0].message.content

    def __del__(self):
        self.close_connection()
