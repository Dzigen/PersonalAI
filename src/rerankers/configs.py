from .methods import EnsembleFusionReranker, MultiStepReranker, SingleStepReranker

AVAILABLE_RETRIEVER_METHODS = {
    'single_step': SingleStepReranker,
    'multi_step': MultiStepReranker,
    'ensemble_fusion': EnsembleFusionReranker
}
