from dataclasses import dataclass, field

from .extractor import LLMExtractorConfig
from .updator import LLMUpdatorConfig

@dataclass
class MemPipelineConfig:
    extractor_config: LLMExtractorConfig = field(default_factory=lambda: LLMExtractorConfig())
    updator_config: LLMUpdatorConfig = field(default_factory=lambda: LLMUpdatorConfig())