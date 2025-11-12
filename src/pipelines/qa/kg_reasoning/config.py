from typing import Dict
from .utils import AbstractKGReasoner, BaseKGReasonerConfig
from .weak_reasoner import WeakKGReasoner, WeakKGReasonerConfig
from .medium_reasoner import MediumKGReasoner, MediumKGReasonerConfig

KGR_MAIN_LOG_PATH = 'log/qa/kg_reasoner/main'

AVAILABLE_KGR_CONFIGS: Dict[str, BaseKGReasonerConfig] = {
    'weak': WeakKGReasonerConfig,
    'medium': MediumKGReasonerConfig,
    'strong': ...
}

AVAILABLE_KG_REASONERS: Dict[str, AbstractKGReasoner] = {
    'weak': WeakKGReasoner,
    'medium': MediumKGReasoner,
    'strong': ...
}
