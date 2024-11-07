import requests
from ..utils import AbstractAgentConnector, AgentConnectorConfig

DEFAULT_LLAMA_CONFIG = AgentConnectorConfig(
    gen_strategy={'max_new_tokens': 2048},
    credentials={'host': 'http://localhost:45678', 'generate_merhod': 'generate', 'check_method': ''})

class LlamaConnector(AbstractAgentConnector):
    def __init__(self, config: AgentConnectorConfig = DEFAULT_LLAMA_CONFIG) -> None:
        self.config = config

    def check_connection(self) -> bool:
        """_summary_

        :return: _description_
        :rtype: bool
        """

        url = f"{self.config.credentials['host']}/{self.config.credentials['check_method']}"
        response = requests.get(url)
        return response.status_code == 200

    def generate(self, system_prompt: str, user_prompt: str, assistant_prompt: str = None) -> str:
        """_summary_

        :param system_prompt: _description_
        :type system_prompt: str
        :param user_prompt: _description_
        :type user_prompt: str
        :param assistant_prompt: _description_, defaults to None
        :type assistant_prompt: str, optional
        :raises ValueError: _description_
        :return: _description_
        :rtype: str
        """

        url = f"{self.config.credentials['host']}/{self.config.credentials['generate_method']}"

        body = {"user_prompt": user_prompt}
        body["system_prompt"] = system_prompt
        body["gen_strategy"] = self.config.gen_strategy
        if assistant_prompt is not None:
            body["assistant_prompt"] = assistant_prompt

        response = requests.post(url, json=body)

        if response.status_code == 200:
            output = response.json()['generated_output']
        else:
            raise ValueError

        return output
