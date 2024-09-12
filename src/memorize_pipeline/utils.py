from dataclasses import dataclass, field

from .extractor import LLMExtractorConfig
from .updator import LLMUpdatorConfig
from ..utils import Logger

log_path = "debug"

@dataclass
class MemPipelineConfig:
    extractor_config: LLMExtractorConfig = field(default_factory=lambda: LLMExtractorConfig())
    updator_config: LLMUpdatorConfig = field(default_factory=lambda: LLMUpdatorConfig())
    log: Logger = field(default_factory=lambda: Logger(log_path))