from typing import Dict, Union
from dataclasses import dataclass
from copy import deepcopy

from .utils import BaseRerankerModuleConfig
from .methods.utils import AbstractRerankerModule
from .configs import AVAILABLE_RETRIEVER_METHODS
from ..db_drivers.vector_driver import VectorComposer
from ..utils.data_structs import BaseConfigOperations


@dataclass
class RerankerDriverConfig(BaseConfigOperations):
    """Конфигурация драйвера переранжирования (reranker driver).

    :param name: Имя стратегии, которая будет использована. Допустимые значения: 'single_step', 'multi_step', 'ensemble_fusion'.
    :type name: str
    :param strategy_config: Конфигурация выбранной стратегии ранжирования, либо словарь с её параметрами, который будет преобразован в конкретный подкласс BaseRerankerModuleConfig.
    :type strategy_config: Union[Dict, BaseRerankerModuleConfig]
    """
    name: str  # 'single_step' | 'multi_step' | 'ensemble_fusion'
    strategy_config: Union[Dict, BaseRerankerModuleConfig]

    def to_str(self) -> str:
        self.formate_fields()
        return f"{self.name}:{self.strategy_config.to_str()}"

    @staticmethod
    def from_dict(dict_config: Dict):
        dictconfig_copy = deepcopy(dict_config)
        formated_config = RerankerDriverConfig(**dictconfig_copy)
        formated_config.formate_fields()
        return formated_config

    def formate_fields(self):
        if isinstance(self.strategy_config, dict):
            self.strategy_config: BaseRerankerModuleConfig = \
                AVAILABLE_RETRIEVER_METHODS[self.name]['config'].from_dict(self.strategy_config)


class RerankerDriver:
    """Компонента для инициализации модуля переранжирования по заданной конфигурации.

    Использует AVAILABLE_RETRIEVER_METHODS для выбора подходящего класса reranker'а и его конфигурации.
    """
    @staticmethod
    def specify(config: Union[Dict, RerankerDriverConfig], vdb_composer: VectorComposer) -> AbstractRerankerModule:
        """Создаёт и настраивает модуль переранжирования на основе заданной конфигурации.

        :param config: Конфигурация драйвера (RerankerDriverConfig) либо словарь с её параметрами.
        :type config: Union[Dict, RerankerDriverConfig]
        :param vdb_composer: Компонента для работы с векторным хранилищем, которая будет передана в конструктор выбранного модуля переранжирования.
        :type vdb_composer: VectorComposer
        :return: Инициализированный модуль переранжирования, реализующий интерфейс AbstractRerankerModule.
        :rtype: AbstractRerankerModule
        """
        if isinstance(config, dict):
            config = RerankerDriverConfig.from_dict(config)
        else:
            config.formate_fields()

        return AVAILABLE_RETRIEVER_METHODS[config.name]['class'](config.strategy_config, vdb_composer)
