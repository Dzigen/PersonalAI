from ..agents import AgentDriverConfig
from ..db_drivers.vector_driver import EmbedderModelConfig

KG_MAIN_LOG_PATH = 'log/kg_model/main'


DEFAULT_EMBEDDERS_CONFIG = {
    'm-e5-small': EmbedderModelConfig()  # по умолчанию в EmbedderModelConfig стоит m-e5-small
}

DEFAULT_EMBEDDERS_MAP = {
    'KnowledgeGraphModel': {
        'EmbeddingsModel': 'm-e5-small',
        'NodesTreeModel': 'm-e5-small'
    }
}

DEFAULT_AGENTS_CONFIG = {
    'llama3.1:8b': AgentDriverConfig()  # по умолчанию в AgentDriverConfig стоит коннектор к ollama-контейнеру с llama3.1:8b-моделью
}

DEFAULT_AGENTS_MAP = {
    'KnowledgeGraphMode': {
        'NodesTreeModel': 'llama3.1:8b'
    },
    'QAPipeline': {
        'general': 'llama3.1:8b'
    },
    'MemPipeline': {
        'general': 'llama3.1:8b'
    }
}
