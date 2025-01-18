from dataclasses import dataclass, field
from typing import Tuple

from ....utils import ReturnInfo, Logger
from ....kg_model import KnowledgeGraphModel
from .weak_reasoner import WeakKGReasonerConfig
from .config import KGR_MAIN_LOG_PATH, AVAILABLE_KG_REASONERS
from .utils import BaseKGReasonerConfig

@dataclass
class KnowledgeGraphReasonerConfig:
    reasoner_name: str = 'weak'
    reasoner_hyperparameters: BaseKGReasonerConfig = field(default_factory=lambda: WeakKGReasonerConfig())
    log: Logger = field(default_factory=lambda: Logger(KGR_MAIN_LOG_PATH))
    verbose: bool = False

class KnowledgeGraphReasoner:
    def __init__(self, kg_model: KnowledgeGraphModel, config: KnowledgeGraphReasonerConfig = KnowledgeGraphReasonerConfig()):
        self.config = config
        self.reasoner = AVAILABLE_KG_REASONERS[self.config.reasoner_name](kg_model, self.config.reasoner_hyperparameters)

    def perform(self, query: str) -> Tuple[str, ReturnInfo]:
        answer, info = self.reasoner.perform(query)
        return answer, info
