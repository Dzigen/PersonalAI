from dataclasses import dataclass

from ....utils import BaseTaskSolvers
from .....utils.task_solver import AgentTaskSolver


@dataclass
class QueryDecomposerTaskSolvers(BaseTaskSolvers):
    decompose_classifier_solver: AgentTaskSolver
    q_decomposition_solver: AgentTaskSolver
