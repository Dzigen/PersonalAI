from dataclasses import dataclass
from .....utils import BaseTaskSolvers
from ......utils import AgentTaskSolver


@dataclass
class MediumPlanEnhancerTaskSolvers(BaseTaskSolvers):
    plan_initialing_solver: AgentTaskSolver
    enhance_classify_solver: AgentTaskSolver
    plan_enhancing_solver: AgentTaskSolver
