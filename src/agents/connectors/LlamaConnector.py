import requests


from ..utils import AbstractAgentConnector, AgentConnectorConfig

DEFAULT_LLAMA_CONFIG = AgentConnectorConfig(
    gen_strategy={'max_new_tokens': 2048},
    credentials={'host': 'http://localhost:45678', 'generate_merhod': 'generate', 'check_method': ''})

class LlamaConnector(AbstractAgentConnector):
    def __init__(self, config: AgentConnectorConfig = DEFAULT_LLAMA_CONFIG) -> None:
        self.config = config

    def check_connection(self) -> bool:
        """Метод для проверка на наличие запущенного api с llm-агентом,
        который готов принимать и обробатывать запросы.

        Returns:
            bool: Если True, то api с llm-агентов в работоспособном состоянии, иначе False.
        """

        url = f"{self.config.credentials['host']}/{self.config.credentials['check_method']}"
        response = requests.get(url)
        return response.status_code == 200

    def generate(self, system_prompt: str, user_prompt: str, assistant_prompt: str = None) -> str:
        """Метод для отправки текстовых звапросов llm-агенту для получения сгенерированных ответов.

        Args:
            user_prompt (str): Запрос для llm-агента.
            assistant_prompt (str, optional): Дополнительная к user_prompt-запросу информация,
                                              которая может быть использована llm-агентом при генерации ответа. Defaults to None.
            gen_strategy (Dict, optional): Стретегия генерации текстовой последовательности для llm-агента. Defaults to None.

        Raises:
            ValueError: От api c llm-агентов пришёл ответ со status_code-значением, отличным от 200.

        Returns:
            str: Текстовая последовательность, сгенерированная llm-агентом.
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
