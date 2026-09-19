from ollama import Client
from typing import Union, Dict, Tuple
import gc
from time import time, sleep
from httpx import ConnectError, RemoteProtocolError, ConnectTimeout, ReadTimeout, ReadError

from .configs import DEFAULT_OLLAMA_CONFIG
from ..utils import AbstractAgentConnector, AgentConnectorConfig, LLMInferenceStat

# available models
# llama3.2 (3B)
# mistral (7B)
# gemma2 (9B)


class OLlamaConnector(AbstractAgentConnector):
    def __init__(self, config: Union[Dict, AgentConnectorConfig] = DEFAULT_OLLAMA_CONFIG) -> None:
        if isinstance(config, dict):
            config = AgentConnectorConfig.from_dict(config)
        else:
            config.formate_fields()
        self.config: AgentConnectorConfig = config

        # костыль
        if 'top_p' in self.config.gen_strategy:
            self.config.gen_strategy['top_p'] = float(self.config.gen_strategy['top_p'])

        self.CONNECTOR_KW = 'ollama'
        self.trials = config.ext_params.get('trials', 5)

        self.open_connection()

    def open_connection(self):
        self.client = Client(
            host=f"http://{self.config.credentials['host']}:{self.config.credentials['port']}",
            timeout=self.config.ext_params['timeout'])

    def check_connection(self) -> bool:
        pass

    def close_connection(self):
        try:
            self.client._client.close()
            del self.client
            gc.collect()
        except (ResourceWarning, AttributeError, TypeError):
            pass

    def generate(self, system_prompt: str, user_prompt: str, assistant_prompt: str = None,
                 gen_strategy: Union[None, Dict[str, str]] = None) -> Tuple[str, LLMInferenceStat]:
        msgs = [{'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt}]
        if assistant_prompt is not None:
            msgs.append({'role': 'assistant', 'content': assistant_prompt})
        gen_strategy = self.config.gen_strategy if gen_strategy is None else gen_strategy

        ai_start_time = time()
        flag, counter = True, 0
        while flag:
            try:
                raw_output = self.client.chat(
                    model=self.config.credentials['model'],
                    options=gen_strategy, messages=msgs,
                    keep_alive=self.config.ext_params['keep_alive']
                )
                flag = False
            except (ConnectError, RemoteProtocolError, ConnectTimeout, ReadTimeout, ReadError, RuntimeError) as e:
                counter += 1
                if counter > self.trials:
                    raise ConnectError(str(e))
                else:
                    self.close_connection()
                    sleep(1)
                    self.open_connection()
        ai_end_time = time()

        inference_info = LLMInferenceStat(
            prompt_tokens_amount=raw_output.get('prompt_eval_count', 0), # !!! PAY ATTENTION !!!
            generated_tokens_amount=raw_output.get('eval_count', 0),
            inference_elapsed_time=round(ai_end_time - ai_start_time, 2)
        )

        # if raw_output.get('prompt_eval_duration', None) is None:
        #     # prompt was cached
        #     pass

        response = raw_output['message']['content']
        return response, inference_info

    def __del__(self):
        self.close_connection()
