from typing import Union, Dict
from dataclasses import fields
from abc import ABC, abstractmethod
from ...pipelines.utils import BaseStages, BaseTaskSolvers
from ..task_solver import AgentTaskSolver


class AbstractAgentStatOperations(ABC):
    tasks_solvers: Union[None, BaseTaskSolvers] = None
    stages: Union[None, BaseStages] = None

    @abstractmethod
    def get_agent_tgen_stat(self) -> Dict[str, Union[None, Dict]]:
        pass

    @abstractmethod
    def clear_agent_tgen_stat(self) -> None:
        pass


class AgentStatOperations(AbstractAgentStatOperations):

    def get_agent_tgen_stat(self) -> Dict[str, Union[None, Dict]]:
        cache_info = dict()

        if self.stages is not None:
            for field in fields(self.stages):
                stage = getattr(self.stages, field.name)
                if issubclass(type(stage), AbstractAgentStatOperations):
                    cache_info[field.name] = stage.get_agent_tgen_stat()

        if self.tasks_solvers is not None:
            for field in fields(self.tasks_solvers):
                task_solver: AgentTaskSolver = getattr(self.tasks_solvers, field.name)
                if task_solver.inference_stat_cache is not None:
                    cache_info[field.name] = task_solver.inference_stat_cache.calculate_stat()
                else:
                    cache_info[field.name] = None

        return cache_info

    def clear_agent_tgen_stat(self) -> None:
        if self.stages is not None:
            for field in fields(self.stages):
                stage = getattr(self.stages, field.name)
                if (stage is not None) and (issubclass(type(stage), AbstractAgentStatOperations)):
                    stage.clear_agent_tgen_stat()

        if self.tasks_solvers is not None:
            for field in fields(self.tasks_solvers):
                task: AgentTaskSolver = getattr(self.tasks_solvers, field.name)
                if task.inference_stat_cache is not None:
                    task.inference_stat_cache.clear()
