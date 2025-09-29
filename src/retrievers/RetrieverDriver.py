from dataclasses import dataclass, field

from .utils import BaseRetrieverModuleConfig
from .methods.utils import AbstractRetriverModule
from .configs import DEFAULT_RETREIVER_CONFIGS, AVAILABLE_RETRIEVER_METHODS


@dataclass
class RetriverDriverConfig:
    # TODO
    pass


class RetriverDriver:
    @staticmethod
    def specify(config: RetriverDriverConfig = RetriverDriverConfig()) -> AbstractRetriverModule:
        # TODO
        pass
