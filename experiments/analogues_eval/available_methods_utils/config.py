from typing import Dict
from .utils import GraphRAGBuildOperations, GraphRAGMINEOperations, GraphRAGQAOperations

AVAILABLE_GRAPHRAG_BUILD_METHODS: Dict[str, GraphRAGBuildOperations] = {
    'hipporag2': ...,
    'kggen': ...,
    'raptor': ...,
    'wikontic': ...,
    'zep': ...
}

AVAILABLE_GRAPHRAG_QA_METHOD: Dict[str, GraphRAGQAOperations] = {
    'hipporag2': ...,
    'kggen': ...,
    'raptor': ...,
    'wikontic': ...,
    'zep': ...
}

AVAILABLE_GRAPHRAG_MINE_METHOD: Dict[str, GraphRAGMINEOperations] = {
    'wikontic': ...,
    'kggen': ...
}
