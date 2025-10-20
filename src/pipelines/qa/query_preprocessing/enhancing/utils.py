from dataclasses import dataclass

from ....utils import BaseTaskSolvers
from .....utils.task_solver import AgentTaskSolver


@dataclass
class QueryEnhancerTaskSolvers(BaseTaskSolvers):
    queryexpansion_solver: AgentTaskSolver
    termscheck_solver: AgentTaskSolver
    linguistcheck_solver: AgentTaskSolver
