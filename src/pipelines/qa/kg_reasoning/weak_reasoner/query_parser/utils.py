from dataclasses import dataclass
from typing import Union

from .....utils import BaseTaskSolvers
from ......utils import AgentTaskSolver


@dataclass
class WeakQueryParserTaskSolvers(BaseTaskSolvers):
    kw_extraction_solver: AgentTaskSolver
