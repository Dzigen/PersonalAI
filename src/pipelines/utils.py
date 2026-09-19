from dataclasses import dataclass, fields
from ..utils import AgentTaskSolver


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
