from dataclasses import dataclass

from ...utils import BaseTaskSolvers
from ....utils import AgentTaskSolver


@dataclass
class MemUpdatorTaskSolvers(BaseTaskSolvers):
    replace_simple_solver: AgentTaskSolver
    replace_hyper_solver: AgentTaskSolver
