from .connectors import MilvusVectorConnector, ChromaVectorConnection
from .connectors.configs import DEFAULT_CHROMA_CONFIG, DEFAULT_MILVUS_CONFIG


DEFAULT_VECTORDB_CONFIGS = {
    'chroma': DEFAULT_CHROMA_CONFIG,
    'milvus': DEFAULT_MILVUS_CONFIG
}

AVAILABLE_VECTORDB_CONNECTORS = {
    'chroma': ChromaVectorConnection,
    'milvus': MilvusVectorConnector
}
