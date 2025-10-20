from dataclasses import dataclass

from ....utils import BaseTaskSolvers
from .....utils.task_solver import AgentTaskSolver


@dataclass
class QueryDenoiserTaskSolvers(BaseTaskSolvers):
    swremoval_solver: AgentTaskSolver
    grammar_check_solver: AgentTaskSolver
