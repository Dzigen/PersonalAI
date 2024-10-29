from .connectors.GigaChatConnector import GigaChatConnector, DEFAULT_GIGACHAT_CONFIG
from .connectors.LlamaConnector import LlamaConnector, DEFAULT_LLAMA_CONFIG
from .connectors.OpenAIConnector import OpenAIConnector, DEFAULT_OPENAI_CONFIG
from .connectors.LocalAgentConnector import LocalAgentConnector, DEFAULT_LOCALAGENT_CONFIG

#
DEFAULT_AGENT_CONFIGS = {
    'local_agent':  DEFAULT_LOCALAGENT_CONFIG,
    'llama': DEFAULT_LLAMA_CONFIG,
    'gigachat':  DEFAULT_GIGACHAT_CONFIG,
    'openai': DEFAULT_OPENAI_CONFIG
}

#
AVAILABLE_AGENT_CONNECTORS = {
    'local_agent': LocalAgentConnector,
    'llama': LlamaConnector,
    'gigachat': GigaChatConnector,
    'openai': OpenAIConnector
}
