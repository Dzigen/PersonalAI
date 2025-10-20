from dataclasses import dataclass

from ...utils import BaseTaskSolvers
from ....utils.task_solver import AgentTaskSolver


@dataclass
class AnswerAggregatorTaskSolvers(BaseTaskSolvers):
    subanswers_summarisation_solver: AgentTaskSolver
