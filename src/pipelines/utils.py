from dataclasses import dataclass, fields
from abc import ABC, abstractmethod
from typing import Union, Dict
from ..utils import Logger
from ..utils import AgentTaskSolverConfig

@dataclass
class BaseStages:
    pass


@dataclass
class BaseTaskSolvers:
    pass

class BaseAgentTaskConfigSelector(ABC):
    @staticmethod
    @abstractmethod
    def get_available_configs() -> None:
        pass

    @staticmethod
    @abstractmethod
    def select(base_config_version: str, cache_table_name: str, inferencestat_table_name: str) -> AgentTaskSolverConfig:
        pass

@dataclass
class BaseAgentTasksConfig:
    task_to_selector_mapping: Dict[str, BaseAgentTaskConfigSelector]

    def to_str(self):
        stringified_config = []
        fields_iterator = fields(self)
        for field_object in fields_iterator:
            if field_object.name == 'task_to_selector_mapping':
                continue

            field_value = getattr(self, field_object.name)

            if type(field_value) is str:
                stringified_config.append(f"{field_object.name}={field_value}")
            elif type(field_value) is AgentTaskSolverConfig:
                stringified_config.append(f"{field_object.name}={field_value.version}")
            else:
                raise TypeError
        
        return ";".join(stringified_config)

    def versions_to_configs(self):
        fields_iterator = fields(self)
        for field_object in fields_iterator:
            if field_object.name == 'task_to_selector_mapping':
                continue

            field_value = getattr(self, field_object.name)

            if type(field_value) is str:
                task_config_version = field_value
                agent_task_config = self.task_to_selector_mapping[field_object.name].select(base_config_version=task_config_version)
                setattr(self, field_object.name, agent_task_config)
