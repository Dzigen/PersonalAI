from typing import Dict
from dataclasses import dataclass

from .utils import BaseRerankerModuleConfig
from .methods.utils import AbstractRerankerModule
from .configs import AVAILABLE_RETRIEVER_METHODS
from ..db_drivers.vector_driver.utils import AbstractVectorDatabaseConnection


@dataclass
class RerankerDriverConfig:
    name: str  # 'single_step' | 'multi_step' | 'ensemble_fusion'
    strategy_config: BaseRerankerModuleConfig


class RerankerDriver:
    @staticmethod
    def specify(config: RerankerDriverConfig,
                dbconn_map: Dict[str, AbstractVectorDatabaseConnection]) -> AbstractRerankerModule:
        return AVAILABLE_RETRIEVER_METHODS[config.name](config.strategy_config, dbconn_map)
