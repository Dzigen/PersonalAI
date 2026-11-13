from dataclasses import dataclass, fields
from ..utils import AgentTaskSolver
from ..environment.EnvironmentConnectionUtils import EnvironmentConnectionUtils


@dataclass
class BaseStages(EnvironmentConnectionUtils):
    pass


@dataclass
class BaseTaskSolvers(EnvironmentConnectionUtils):
    pass
