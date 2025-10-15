from dataclasses import dataclass
from .....utils import BaseTaskSolvers
from ......utils import AgentTaskSolver


@dataclass
class MediumASummarizerTaskSolvers(BaseTaskSolvers):
    clueanswers_summ_solver: AgentTaskSolver
