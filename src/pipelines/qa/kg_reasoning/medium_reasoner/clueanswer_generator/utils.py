from dataclasses import dataclass
from .....utils import BaseTaskSolvers
from ......utils import AgentTaskSolver


@dataclass
class MediumCAGeneratorTaskSolvers(BaseTaskSolvers):
    cagen_solver: AgentTaskSolver
