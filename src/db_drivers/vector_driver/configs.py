from .connectors import ChromaConnection, DEFAULT_CHROMA_CONFIG

DEFAULT_VECTORDB_CONFIGS = {
    'chroma': DEFAULT_CHROMA_CONFIG,
}

AVAILABLE_VECTORDB_CONNECTORS = {
    'chroma': ChromaConnection,
}