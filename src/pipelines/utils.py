from dataclasses import dataclass
from ..utils import Logger


@dataclass
class BaseStages:
    pass


@dataclass
class BaseTaskSolvers:
    pass


@dataclass
class BasePipelineComponentConfig:
    lang: str
    verbose: bool
    log: Logger

    def synchronize_language(self):
        # TODO
        pass
