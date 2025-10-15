from dataclasses import dataclass
from .....utils import BaseTaskSolvers
from ......utils import AgentTaskSolver


@dataclass
class MediumCQGeneratorTaskSolvers(BaseTaskSolvers):
    cluequery_gen_solver: AgentTaskSolver
