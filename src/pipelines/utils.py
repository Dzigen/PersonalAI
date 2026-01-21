from dataclasses import dataclass, fields
from abc import ABC, abstractmethod
from typing import Union, Dict, List, Tuple
from ..utils import AgentTaskSolverConfig, AgentTaskSolver
from ..utils.data_structs import BaseConfigOperations


@dataclass
class BaseStages:

    def close_connections(self):
        fields_iterator = fields(self)
        for stage in fields_iterator:
            stage_inst = getattr(self, stage.name)
            # print(stage.name, type(stage_inst))
            try:
                stage_inst.stages.close_connections()
                # print(stage.name, type(stage_inst.stages))
            except AttributeError:
                pass
            try:
                stage_inst.tasks_solvers.close_connections()
                # print(stage.name, type(stage_inst.tasks_solvers))
            except AttributeError:
                pass
            try:
                stage_inst.cachekv.close_connection()
                # print(stage.name, type(stage_inst.cachekv))
            except (AttributeError, TypeError):
                pass


@dataclass
class BaseTaskSolvers:

    def close_connections(self):
        fields_iterator = fields(self)
        for llmtask_field in fields_iterator:
            spec_agent: AgentTaskSolver = getattr(self, llmtask_field.name)

            if spec_agent.cachekv is not None:
                spec_agent.cachekv.close_connection()
            if spec_agent.inference_stat_cache is not None:
                spec_agent.inference_stat_cache.close_connection()


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
class BaseAgentTasksConfig(BaseConfigOperations):
    task_to_selector_mapping: Dict[str, BaseAgentTaskConfigSelector]

    @staticmethod
    def from_dict(dict_config: Dict):
        pass

    def to_str(self):
        stringified_config = []
        fields_iterator = fields(self)
        for field_object in fields_iterator:
            if field_object.name == 'task_to_selector_mapping':
                continue

            field_value = getattr(self, field_object.name)

            if isinstance(field_value, str):
                stringified_config.append(f"{field_object.name}={field_value}")
            elif isinstance(field_value, AgentTaskSolverConfig):
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

            if isinstance(field_value, str):
                task_config_version = field_value
                agent_task_config = self.task_to_selector_mapping[field_object.name].select(base_config_version=task_config_version)
                setattr(self, field_object.name, agent_task_config)
