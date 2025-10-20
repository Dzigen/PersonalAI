from typing import Dict
from dataclasses import dataclass

from .utils import BaseRerankerModuleConfig
from .methods.utils import AbstractRerankerModule
from .configs import AVAILABLE_RETRIEVER_METHODS
from ..db_drivers.vector_driver import VectorComposer


@dataclass
class RerankerDriverConfig:
    name: str  # 'single_step' | 'multi_step' | 'ensemble_fusion'
    strategy_config: BaseRerankerModuleConfig

    def to_str(self) -> str:
        return f"{self.name}:{self.strategy_config.to_str()}"


class RerankerDriver:
    @staticmethod
    def specify(config: RerankerDriverConfig, vdb_composer: VectorComposer) -> AbstractRerankerModule:
        return AVAILABLE_RETRIEVER_METHODS[config.name](config.strategy_config, vdb_composer)
