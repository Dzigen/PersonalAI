import os
from openai import OpenAI

from ..utils import AbstractAgentConnector, AgentConnectorConfig


DEEPSEEK_KEY = 'sk-7114ae174a6142bf8b028e8bf6af9579'
DEEPSEEK_CONFIG = AgentConnectorConfig(
    gen_strategy={'max_tokens': 4096, 'seed': 42, 'top_p': 10e-16, 'temperature': 0.0, 'frequency_penalty':0, 'presence_penalty':0},
    credentials={'token': DEEPSEEK_KEY, 'model': 'deepseek-chat', 'base_url': 'https://api.deepseek.com'})

GPT4OMINI_KEY = "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"
GPT4OMINI_CONFIG = AgentConnectorConfig(
    gen_strategy={'max_tokens': 4096, 'seed': 42, 'top_p': 10e-16, 'temperature': 0.0, 'frequency_penalty':0, 'presence_penalty':0},
    credentials={'token': GPT4OMINI_KEY, 'model': 'gpt-4o-mini', 'base_url': None})


class OpenAIConnector(AbstractAgentConnector):
    def __init__(self, config: AgentConnectorConfig = GPT4OMINI_KEY) -> None:
        self.model = config.credentials['model']
        self.gen_strategy = config.gen_strategy
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", config.credentials['token']),
                             base_url=config.credentials['base_url'])

    def check_connection(self):
        # TODO
        pass

    def close_connection(self):
        self.client.close()

    def generate(self, system_prompt: str, user_prompt: str, assistant_prompt: str = None) -> str:
        msgs = [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]
        if assistant_prompt is not None:
            msgs.append({"role": "assistant", "content": assistant_prompt})

        completion = self.client.chat.completions.create(
            model=self.model, messages=msgs, **self.gen_strategy)

        return completion.choices[0].message.content
