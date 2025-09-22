from typing import Union, Dict
from gigachat import GigaChat
from gigachat.exceptions import ResponseError
from gigachat.models import Chat, Messages
from httpx import ConnectError, RemoteProtocolError

# https://github.com/VRSEN/agency-swarm/issues/99
# https://github.com/ai-forever/gigachat/blob/main/src/gigachat/client.py#L182

from .configs import DEFAULT_GIGACHAT_CONFIG
from ..utils import AbstractAgentConnector, AgentConnectorConfig


class GigaChatConnector(AbstractAgentConnector):
    def __init__(self, config: AgentConnectorConfig = DEFAULT_GIGACHAT_CONFIG) -> None:
        self.gen_strategy = config.gen_strategy
        self.trials = config.ext_params['trials']
        self.config = config
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
        self.giga_model.close()

    def generate(self, system_prompt: str, user_prompt: str, assistant_prompt: str = None, gen_strategy: Union[None, Dict[str, str]] = None) -> str:
        msgs = [Messages(role='system', content=system_prompt),
                Messages(role='user', content=user_prompt)]
        if assistant_prompt is not None:
            msgs.append(Messages(role='assistant', content=assistant_prompt))

        gen_strategy = self.gen_strategy if gen_strategy is None else gen_strategy
        chat = Chat(messages=msgs, **gen_strategy)

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

        return response.choices[0].message.content

    def __del__(self):
        self.close_connection()
