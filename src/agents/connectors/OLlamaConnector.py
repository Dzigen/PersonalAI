from ollama import Client
from typing import Union, Dict, Tuple
import gc
from time import time

from .configs import DEFAULT_OLLAMA_CONFIG
from ..utils import AbstractAgentConnector, AgentConnectorConfig, LLMInferenceStat

# available models
# llama3.2 (3B)
# mistral (7B)
# gemma2 (9B)


class OLlamaConnector(AbstractAgentConnector):
    def __init__(self, config: AgentConnectorConfig = DEFAULT_OLLAMA_CONFIG) -> None:
        self.config = config
        self.open_connection()
        self.CONNECTOR_KW = 'ollama'

    def open_connection(self):
        self.client = Client(
            host=f"http://{self.config.credentials['host']}:{self.config.credentials['port']}",
            timeout=self.config.ext_params['timeout'])

    def check_connection(self) -> bool:
        pass

    def close_connection(self):
        try:
            del self.client
        except AttributeError:
            pass
        gc.collect()

    def generate(self, system_prompt: str, user_prompt: str, assistant_prompt: str = None,
                 gen_strategy: Union[None, Dict[str, str]] = None) -> Tuple[str, LLMInferenceStat]:
        pp_start_time = time()
        msgs = [{'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt}]
        if assistant_prompt is not None:
            msgs.append({'role': 'assistant', 'content': assistant_prompt})
        gen_strategy = self.config.gen_strategy if gen_strategy is None else gen_strategy
        pp_end_time = time()

        ai_start_time = time()
        raw_output = self.client.chat(
            model=self.config.credentials['model'],
            options=gen_strategy,
            messages=msgs,
            keep_alive=self.config.ext_params['keep_alive'])
        ai_end_time = time()

        inference_info = LLMInferenceStat(
            prompt_tokens_amount=raw_output['prompt_eval_count'],
            generated_tokens_amount=raw_output['eval_count'],
            preparation_elapsed_time=round(pp_end_time - pp_start_time, 2),
            inference_elapsed_time=round(ai_end_time - ai_start_time, 2)
        )

        response = raw_output['message']['content']
        return response, inference_info

    def __del__(self):
        self.close_connection()
