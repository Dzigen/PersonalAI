from abc import abstractmethod
from dataclasses import dataclass, field
from copy import deepcopy

from typing import Dict, Union, Tuple
from ..agent_stat_analyzer.utils import LLMInferenceStat
from ..data_structs import BaseConfigOperations


@dataclass
class AgentConnectorConfig(BaseConfigOperations):
    """Конфигурация коннектора к LLM-агенту.

    :param gen_strategy: Набор гиперпараметров генерации текста, который будет передаваться в конкретный коннектор (температура, top_k и тд).
    :type gen_strategy: Dict
    :param credentials: Параметры авторизации и идентификации модели (API-ключ, базовый URL и тд).
    :type credentials: Dict
    :param ext_params: Прочие внешние параметры работы коннектора (таймауты, число ретраев и тд).
    :type ext_params: Dict
    """
    gen_strategy: Dict = field(default_factory=lambda: dict())
    credentials: Dict = field(default_factory=lambda: dict())
    ext_params: Dict = field(default_factory=lambda: dict())

    def to_str(self):
        """Формирует строковое представление конфигурации коннектора.

        :return: Строка, однозначно кодирующая текущий набор параметров.
        :rtype: str
        """
        str_genstrat = ";".join(list(map(lambda p: f"{p[0]}={p[1]}", sorted(
            [(k, str(v)) for k, v in self.gen_strategy.items()], key=lambda p: p[0]))))
        str_creds = ";".join(list(map(lambda p: f"{p[0]}={p[1]}", sorted(
            [(k, str(v)) for k, v in self.credentials.items() if k not in ['host', 'port']], key=lambda p: p[0]))))
        return f"{str_genstrat}|{str_creds}"

    @staticmethod
    def from_dict(dict_config: Dict):
        """Создаёт экземпляр AgentConnectorConfig на основе словаря.

        :param dict_config: Словарь с ключами, соответствующими полям конфигурации коннектора.
        :type dict_config: Dict
        :return: Нормализованная конфигурация коннектора.
        :rtype: AgentConnectorConfig
        """
        dictconfig_copy = deepcopy(dict_config)
        formated_config = AgentConnectorConfig(**dictconfig_copy)
        formated_config.formate_fields()
        return formated_config


class AbstractAgentConnector:
    """Абстрактный интерфейс коннектора к LLM-агенту.

    Реализации этого класса инкапсулируют детали обращения к конкретному провайдеру (локальная модель, OpenAI, GigaChat, Ollama и т.д.),
    но предоставляют единый интерфейс для остальных компонентов системы.

    :param CONNECTOR_KW: Уникальный ключ, идентифицирующий конкретный тип коннектора.
    :type CONNECTOR_KW: Union[None, str]
    :param config: Конфигурация коннектора к LLM-агенту.
    :type config: Union[None, AgentConnectorConfig]
    """
    CONNECTOR_KW: Union[None, str] = None
    config: Union[None, AgentConnectorConfig] = None

    @abstractmethod
    def check_connection(self) -> bool:
        """Проверяет доступность и корректность соединения с LLM-агентом."""
        pass

    @abstractmethod
    def generate(self, system_prompt: str, user_prompt: str, assistant_prompt: str = None,
                 gen_strategy: Union[None, Dict[str, str]] = None) -> Tuple[str, LLMInferenceStat]:
        """Выполняет один вызов LLM-агента.

        :param system_prompt: System-промпт для LLM-агента.
        :type system_prompt: str
        :param user_prompt: Основной user-промпт с постановкой задачи.
        :type user_prompt: str
        :param assistant_prompt: Дополнительный контекст для уточнения задачи. Значение по умолчанию None.
        :type assistant_prompt: str
        :param gen_strategy: Переопределение стратегии генерации для конкретного вызова. Если None, используются настройки из config.gen_strategy.
        :type gen_strategy: Union[None, Dict[str, str]]
        :return: Кортеж из сгенерированного текста и объекта со статистикой инференса.
        :rtype: Tuple[str, LLMInferenceStat]
        """
        pass

    @abstractmethod
    def close_connection(self) -> None:
        pass

    def __del__(self) -> None:
        self.close_connection()
