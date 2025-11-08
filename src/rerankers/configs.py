from typing import Dict, Union
from .methods import EnsembleFusionReranker, MultiStepReranker, SingleStepReranker, \
    EnsembleFusionRerankerConfig, MultiStepRerankerConfig, SingleStepRerankerConfig
from .methods.utils import AbstractRerankerModule
from .utils import BaseRerankerModuleConfig

AVAILABLE_RETRIEVER_METHODS: Dict[str, Dict[str, Union[AbstractRerankerModule, BaseRerankerModuleConfig]]] = {
    'single_step': {
        'config': SingleStepRerankerConfig,
        'class': SingleStepReranker
    },
    'multi_step': {
        'config': MultiStepRerankerConfig,
        'class': MultiStepReranker
    },
    'ensemble_fusion': {
        'config': EnsembleFusionRerankerConfig,
        'class': EnsembleFusionReranker
    }
}
