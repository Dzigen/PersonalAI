from dataclasses import dataclass
from ..utils import BaseStages
from .extractor import LLMExtractor
from .updator import LLMUpdator


@dataclass
class MemPipelineStages(BaseStages):
    extractor: LLMExtractor
    updator: LLMUpdator
