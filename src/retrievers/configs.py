from .methods.configs import DEFAULT_MULTISTEP_RETRIVER_CONFIG, DEFAULT_RRF_RETRIEVER_CONFIG, DEFAULT_SINGLESTEP_RETRIEVER_CONFIG
from .methods import RRFusionRetriever, MultiStepRetriever, SingleStepRetriever

DEFAULT_RETREIVER_CONFIGS = {
    'singlestep': DEFAULT_SINGLESTEP_RETRIEVER_CONFIG,
    'multistep': DEFAULT_MULTISTEP_RETRIVER_CONFIG,
    'rrf': DEFAULT_RRF_RETRIEVER_CONFIG
}

AVAILABLE_RETRIEVER_METHODS = {
    'singlestep': SingleStepRetriever,
    'multistep': MultiStepRetriever,
    'rrf': RRFusionRetriever
}
