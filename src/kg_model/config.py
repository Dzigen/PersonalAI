from .utils import AgentsMapping, KGEmbeddersMapping
from ..agents import AgentDriverConfig
from ..db_drivers.vector_driver import EmbedderModelConfig

KG_MAIN_LOG_PATH = 'log/kg_model/main'


DEFAULT_EMBEDDERS_CONFIG = {
    'default_embedder': EmbedderModelConfig()  # по умолчанию в EmbedderModelConfig стоит m-e5-base
}

DEFAULT_EMBEDDERS_MAP = KGEmbeddersMapping(
    embeddings_model={'dense_nodes': 'default_embedder', 'dense_triplets': 'default_embedder'},
    nodestree_model={'leaf_dense_nodes': 'default_embedder', 'summ_dense_nodes': 'default_embedder'}
)


DEFAULT_AGENTS_CONFIG = {
    'default_llmagent': AgentDriverConfig()  # по умолчанию в AgentDriverConfig стоит коннектор к ollama-контейнеру с qwen2.5:7b-моделью
}

DEFAULT_AGENTS_MAP = AgentsMapping(
    qa_pipeline='default_llmagent',
    mem_pipeline='default_llmagent',
    kg_nodestree_model='default_llmagent'
)
