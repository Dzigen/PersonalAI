from dataclasses import dataclass
from typing import Union

from .....utils import BaseTaskSolvers
from ......utils import AgentTaskSolver


@dataclass
class WeakAGeneratorTaskSolvers(BaseTaskSolvers):
    answer_generator_solver: AgentTaskSolver
