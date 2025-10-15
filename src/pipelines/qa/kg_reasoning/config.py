from typing import Dict
from .utils import AbstractKGReasoner
from .weak_reasoner import WeakKGReasoner
from .medium_reasoner import MediumKGReasoner

KGR_MAIN_LOG_PATH = 'log/qa/kg_reasoner/main'

AVAILABLE_KG_REASONERS: Dict[str, AbstractKGReasoner] = {
    'weak': WeakKGReasoner,
    'medium': MediumKGReasoner,
    'strong': ...
}
