from .kg_building import Hipporag2BuildOperations
from .qa_eval import Hipporag2QAOperations

HIPPORAG2_INTERFACES = {
    'kgbuild': Hipporag2BuildOperations,
    'qaeval': Hipporag2QAOperations
}
