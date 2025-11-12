from typing import Dict
from dataclasses import dataclass
from ..utils.data_structs import BaseConfigOperations


@dataclass
class BaseRerankerModuleConfig(BaseConfigOperations):

    @staticmethod
    def from_dict(dict_config: Dict):
        pass
