from ollama import Client
from typing import Union, Dict
import gc

from .configs import DEFAULT_OLLAMA_CONFIG
from ..utils import AbstractAgentConnector, AgentConnectorConfig

# available models
# llama3.2 (3B)
# mistral (7B)
# gemma2 (9B)


class OLlamaConnector(AbstractAgentConnector):
    def __init__(self, config: AgentConnectorConfig = DEFAULT_OLLAMA_CONFIG) -> None:
        self.config = config
        self.open_connection()

    def open_connection(self):
        self.client = Client(
            host=f"http://{self.config.ext_params['host']}:{self.config.ext_params['port']}",
            timeout=self.config.ext_params['timeout'])

    def check_connection(self) -> bool:
        pass

    def close_connection(self):
        del self.client
        gc.collect()

    def generate(self, system_prompt: str, user_prompt: str, assistant_prompt: str = None, gen_strategy: Union[None, Dict[str, str]] = None) -> str:

        msgs = [{'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt}]
        if assistant_prompt is not None:
            msgs.append({'role': 'assistant', 'content': assistant_prompt})

        gen_strategy = self.config.gen_strategy if gen_strategy is None else gen_strategy
        raw_output = self.client.chat(
            model=self.config.credentials['model'],
            options=gen_strategy,
            messages=msgs,
            keep_alive=self.config.ext_params['keep_alive'])

        response = raw_output['message']['content']
        return response

    def __del__(self):
        self.close_connection()
