from .kg_building import WikonticBuildOperations
from .qa_eval import WikonticQAOperations
from .kg_eval import WikonticMINEOperations

WIKONTIC_INTERFACES = {
    'kgbuild': WikonticBuildOperations,
    'qaeval': WikonticQAOperations,
    'kgeval_mine': WikonticMINEOperations
}
