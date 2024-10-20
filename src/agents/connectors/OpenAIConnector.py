import os 
from typing import Dict
from openai import OpenAI 

from ..utils import AbstractAgentConnector, AgentConnectorConfig

OPENAI_KEY = "sk-861mINAavom2SSBqgrI82D4thMOfqT37knCof2o0H0T3BlbkFJ2gdVXJuVjNesNNP2aeUwPoBpZP3a3R1gn1kqv97CsA"

DEFAULT_OPENAI_CONFIG = AgentConnectorConfig(
    gen_strategy={},
    credentials={'token': OPENAI_KEY, 'model': 'gpt-4o-mini'})

class OpenAIConnector(AbstractAgentConnector):
    """_summary_

    :param AbstractAgentConnector: _description_
    :type AbstractAgentConnector: _type_
    """
    def __init__(self, config: AgentConnectorConfig = DEFAULT_OPENAI_CONFIG) -> None:
        """_summary_

        :param config: _description_, defaults to DEFAULT_OPENAI_CONFIG
        :type config: AgentConnectorConfig, optional
        """
        self.model = config.credentials['model']
        self.gen_strategy = config['gen_strategy']
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", config.credentials['token']))

    # TODO
    def check_connection(self):
        pass

    def generate(self, system_prompt: str, user_prompt: str, assistant_prompt: str = None) -> str:
        """_summary_

        :param system_prompt: _description_
        :type system_prompt: str
        :param user_prompt: _description_
        :type user_prompt: str
        :param assistant_prompt: _description_, defaults to None
        :type assistant_prompt: str, optional
        :return: _description_
        :rtype: str
        """
        msgs = [{"role": "system", "content": system_prompt}]
        if assistant_prompt is not None:
            msgs.append({"role": "assistant", "content": assistant_prompt})
        msgs.append({"role": "user", "content": user_prompt})

        completion = self.client.chat.completions.create(
            model=self.model, messages=msgs, **self.gen_strategy)

        return completion.choices[0].message.content