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
    'qwen2.5:7b': AgentDriverConfig()  # по умолчанию в AgentDriverConfig стоит коннектор к ollama-контейнеру с qwen2.5:7b-моделью
}

DEFAULT_AGENTS_MAP = AgentsMapping(
    qa_pipeline='qwen2.5:7b',
    mem_pipeline='qwen2.5:7b',
    kg_nodestree_model='qwen2.5:7b'
)
