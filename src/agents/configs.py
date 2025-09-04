from .connectors import LocalAgentConnector, OLlamaConnector, \
    OpenAIConnector, GigaChatConnector, StubAgentConnector

from .connectors.configs import DEFAULT_GIGACHAT_CONFIG, DEFAULT_OLLAMA_CONFIG, \
    GPT4OMINI_CONFIG, DEEPSEEK_CONFIG, DEFAULT_LOCALAGENT_CONFIG, DEFAULT_STUBAGENT_CONFIG

DEFAULT_AGENT_CONFIGS = {
    'local_agent':  DEFAULT_LOCALAGENT_CONFIG,
    'ollama': DEFAULT_OLLAMA_CONFIG,
    'gigachat':  DEFAULT_GIGACHAT_CONFIG,
    'openai': DEEPSEEK_CONFIG,
    'stub': DEFAULT_STUBAGENT_CONFIG
}

AVAILABLE_AGENT_CONNECTORS = {
    'local_agent': LocalAgentConnector,
    'ollama': OLlamaConnector,
    'gigachat': GigaChatConnector,
    'openai': OpenAIConnector,
    'stub': StubAgentConnector
}
