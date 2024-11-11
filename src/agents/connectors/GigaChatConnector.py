from gigachat import GigaChat
from gigachat.models import Chat, Messages

# https://github.com/VRSEN/agency-swarm/issues/99
# https://github.com/ai-forever/gigachat/blob/main/src/gigachat/client.py#L182

from ..utils import AbstractAgentConnector, AgentConnectorConfig

GIGACHAT_KEY = 'OWUwOGUzOWEtMjJiNi00YmMxLThmMmItNzMwNjM2MTI2YmYxOjg2ODdiOTVhLTZkNDctNGFjOC1iMmViLTEyNDA5MmFiN2Q5Mw=='

DEFAULT_GIGACHAT_CONFIG = AgentConnectorConfig(
    gen_strategy={},
    credentials={'token': GIGACHAT_KEY, 'scope': 'GIGACHAT_API_CORP',
                  'model': "GigaChat-Pro", 'verify_ssl_certs': False},
    ext_params={'timeout': 480})

class GigaChatConnector(AbstractAgentConnector):
    """_summary_"""
    def __init__(self, config: AgentConnectorConfig = DEFAULT_GIGACHAT_CONFIG) -> None:
        self.gen_strategy = config.gen_strategy
        self.giga_model = GigaChat(credentials=config.credentials['token'], scope=config.credentials['scope'],
                                   verify_ssl_certs=config.credentials['verify_ssl_certs'], model=config.credentials['model'],
                                   timeout=config.ext_params['timeout'])

    def check_connection(self):
        # TODO
        pass

    def generate(self, system_prompt: str, user_prompt: str, assistant_prompt: str = None) -> str:
        msgs = [Messages(role='system', content=system_prompt)]
        if assistant_prompt is not None:
            msgs.append(Messages(role='assistant', content=assistant_prompt))
        msgs.append(Messages(role='user', content=user_prompt))

        chat = Chat(messages=msgs, **self.gen_strategy)

        response = self.giga_model.chat(chat)
        return response.choices[0].message.content
