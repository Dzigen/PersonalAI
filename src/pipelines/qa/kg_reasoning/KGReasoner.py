from dataclasses import dataclass, field
from typing import Tuple

from ....utils import ReturnInfo, Logger
from .utils import KGR_MAIN_LOG_PATH

@dataclass
class KnowledgeGraphReasonerConfig:
    log: Logger = field(default_factory=lambda: Logger(KGR_MAIN_LOG_PATH))
    verbose: bool = False

class KnowledgeGraphReasoner:
    def __init__(self, config: KnowledgeGraphReasonerConfig):
        pass

    def perform(self, query: str) -> Tuple[str, ReturnInfo]:
        pass
