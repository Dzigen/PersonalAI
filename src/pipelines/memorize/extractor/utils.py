from dataclasses import dataclass

from ...utils import BaseTaskSolvers
from ....utils import AgentTaskSolver


@dataclass
class MemExtractorTaskSolvers(BaseTaskSolvers):
    triplets_extraction_solver: AgentTaskSolver
    thesises_extraction_solver: AgentTaskSolver
