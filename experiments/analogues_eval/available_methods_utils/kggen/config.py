from .kg_building import KGGenBuildOperations
from .kg_eval import KGGenMINEOperations

KGGEN_INTERFACES = {
    'kgbuild': KGGenBuildOperations,
    'kgeval_mine': KGGenMINEOperations
}
