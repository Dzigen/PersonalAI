from .methods.configs import DEFAULT_MULTISTEP_RETRIEVER_CONFIG, DEFAULT_ENSEMBLE_RETRIEVER_CONFIG, DEFAULT_SINGLESTEP_RETRIEVER_CONFIG
from .methods import EnsembleFusionReranker, MultiStepReranker, SingleStepReranker

DEFAULT_RETREIVER_CONFIGS = {
    'single_step': DEFAULT_SINGLESTEP_RETRIEVER_CONFIG,
    'multi_step': DEFAULT_MULTISTEP_RETRIEVER_CONFIG,
    'ensemble_fusion': DEFAULT_ENSEMBLE_RETRIEVER_CONFIG
}

AVAILABLE_RETRIEVER_METHODS = {
    'single_step': SingleStepReranker,
    'multi_step': MultiStepReranker,
    'ensemble_fusion': EnsembleFusionReranker
}
