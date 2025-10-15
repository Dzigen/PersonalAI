from dataclasses import dataclass
from .....utils import BaseTaskSolvers
from ......utils import AgentTaskSolver


@dataclass
class MediumEntitiesExtractorTaskSolvers(BaseTaskSolvers):
    entities_extractor_solver: AgentTaskSolver
