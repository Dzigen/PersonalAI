from typing import Dict
from dataclasses import dataclass
from ..utils.data_structs import BaseConfigOperations


@dataclass
class BaseRerankerModuleConfig(BaseConfigOperations):
    """Базовый класс конфигурации для модулей переранжирования.
    Используется как родительский тип для конкретных конфигов стратегий rerank'а (single_step, multi_step, ensemble).
    """
    @staticmethod
    def from_dict(dict_config: Dict):
        pass
