from typing import Dict
from .utils import GraphRAGBuildOperations, GraphRAGMINEOperations, GraphRAGQAOperations

from .hipporag2 import HIPPORAG2_INTERFACES
from .kggen import KGGEN_INTERFACES
from .raptor import RAPTOR_INTERFACES
from .wikontic import WIKONTIC_INTERFACES
from .lightrag import LIGHTRAG_INTERFACES

AVAILABLE_GRAPHRAG_BUILD_METHODS: Dict[str, GraphRAGBuildOperations] = {
    'hipporag2': HIPPORAG2_INTERFACES['kgbuild'],
    'kggen': KGGEN_INTERFACES['kgbuild'],
    'raptor': RAPTOR_INTERFACES['kgbuild'],
    'wikontic': WIKONTIC_INTERFACES['kgbuild'],
    'lightrag': LIGHTRAG_INTERFACES['kgbuild']
}

AVAILABLE_GRAPHRAG_QA_METHOD: Dict[str, GraphRAGQAOperations] = {
    'hipporag2': HIPPORAG2_INTERFACES['qaeval'],
    'raptor': RAPTOR_INTERFACES['qaeval'],
    'wikontic': WIKONTIC_INTERFACES['qaeval'],
    'lightrag': LIGHTRAG_INTERFACES['qaeval']
}

AVAILABLE_GRAPHRAG_MINE_METHOD: Dict[str, GraphRAGMINEOperations] = {
    'wikontic': WIKONTIC_INTERFACES['kgeval_mine'],
    'kggen': KGGEN_INTERFACES['kgeval_mine']
}
