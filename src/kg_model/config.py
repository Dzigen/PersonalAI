from .utils import AgentsMapping, KGEmbeddersMapping
from ..agents import AgentDriverConfig
from ..db_drivers.vector_driver import EmbedderModelConfig

KG_MAIN_LOG_PATH = 'log/kg_model/main'


DEFAULT_EMBEDDERS_CONFIG = {
    'm-e5-base': EmbedderModelConfig()  # по умолчанию в EmbedderModelConfig стоит m-e5-base
}

DEFAULT_EMBEDDERS_MAP = KGEmbeddersMapping(
    embeddings_model={'dense_nodes': 'm-e5-base', 'dense_triplets': 'm-e5-base'},
    nodestree_model={'leaf_dense_nodes': 'm-e5-base', 'summ_dense_nodes': 'm-e5-base'}
)


DEFAULT_AGENTS_CONFIG = {
    'llama3.1:8b': AgentDriverConfig()  # по умолчанию в AgentDriverConfig стоит коннектор к ollama-контейнеру с llama3.1:8b-моделью
}

DEFAULT_AGENTS_MAP = AgentsMapping(
    qa_pipeline='llama3.1:8b',
    mem_pipeline='llama3.1:8b',
    kg_nodestree_model='llama3.1:8b'
)
