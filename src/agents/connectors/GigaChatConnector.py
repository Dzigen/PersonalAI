from typing import Union, Dict, Tuple
from gigachat import GigaChat
from gigachat.exceptions import ResponseError
from time import time
from gigachat.models import Chat, Messages
from httpx import ConnectError, RemoteProtocolError

# https://github.com/VRSEN/agency-swarm/issues/99
# https://github.com/ai-forever/gigachat/blob/main/src/gigachat/client.py#L182

from .configs import DEFAULT_GIGACHAT_CONFIG
from ..utils import AbstractAgentConnector, AgentConnectorConfig, LLMInferenceStat


class GigaChatConnector(AbstractAgentConnector):
    def __init__(self, config: Union[Dict, AgentConnectorConfig] = DEFAULT_GIGACHAT_CONFIG) -> None:
        if isinstance(config, dict):
            config = AgentConnectorConfig.from_dict(config)
        else:
            config.formate_fields()
        self.config: AgentConnectorConfig = config
        
        # костыль
        if 'top_p' in self.config.gen_strategy:
            self.config.gen_strategy['top_p'] = float(self.config.gen_strategy['top_p'])

        self.trials = config.ext_params['trials']
        self.CONNECTOR_KW = 'gigachat'

        self.open_connection()

    def open_connection(self):
        self.giga_model = GigaChat(
            credentials=self.config.credentials['token'], scope=self.config.credentials['scope'],
            verify_ssl_certs=self.config.ext_params['verify_ssl_certs'], model=self.config.credentials['model'],
            timeout=self.config.ext_params['timeout'])

    def check_connection(self):
        # TODO
        pass

    def close_connection(self):
        try:
            self.giga_model.close()
        except TypeError:
            pass

    def generate(self, system_prompt: str, user_prompt: str, assistant_prompt: str = None,
                 gen_strategy: Union[None, Dict[str, str]] = None) -> Tuple[str, LLMInferenceStat]:
        msgs = [Messages(role='system', content=system_prompt),
                Messages(role='user', content=user_prompt)]
        if assistant_prompt is not None:
            msgs.append(Messages(role='assistant', content=assistant_prompt))

        gen_strategy = self.config.gen_strategy if gen_strategy is None else gen_strategy
        chat = Chat(messages=msgs, **gen_strategy)

        ai_start_time = time()
        flag, counter = True, 0
        while flag:
            try:
                response = self.giga_model.chat(chat)
                flag = False
            except (ConnectError, RemoteProtocolError, ResponseError) as e:
                counter += 1
                if counter > self.trials:
                    raise ConnectError
                else:
                    self.open_connection()
        ai_end_time = time()

        inference_info = LLMInferenceStat(
            prompt_tokens_amount=response.usage.prompt_tokens,
            generated_tokens_amount=response.usage.completion_tokens,
            inference_elapsed_time=round(ai_end_time - ai_start_time, 2)
        )

        return response.choices[0].message.content, inference_info

    def __del__(self):
        self.close_connection()
