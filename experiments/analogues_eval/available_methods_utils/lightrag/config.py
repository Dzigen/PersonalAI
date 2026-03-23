from .kg_building import LightRAGBuildOperations
from .qa_eval import LightRAGQAOperations

LIGHTRAG_INTERFACES = {
    'kgbuild': LightRAGBuildOperations,
    'qaeval': LightRAGQAOperations
}
