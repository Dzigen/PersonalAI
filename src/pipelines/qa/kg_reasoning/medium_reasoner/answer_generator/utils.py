from dataclasses import dataclass
from .....utils import BaseTaskSolvers
from ......utils import AgentTaskSolver


@dataclass
class MediumAGeneratorTaskSolvers(BaseTaskSolvers):
    answer_classify_solver: AgentTaskSolver
    answer_gen_solver: AgentTaskSolver
