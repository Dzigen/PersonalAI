from typing import Dict
from .agent_tasks.query_generator import AgentCQueryGenTaskConfigSelector
from .....utils import BaseAgentTaskConfigSelector

CQGEN_MAIN_LOG_PATH = "log/qa/kg_reasoner/medium/cluequeries_generator/main"
DEFAULT_CQGEN_TASK_CONFIG = AgentCQueryGenTaskConfigSelector.select(
    base_config_version='v1')

CQGEN_AGENTASKS_SELECTORS_MAPPING: Dict[str, BaseAgentTaskConfigSelector] = {
    'cquerie_generator': AgentCQueryGenTaskConfigSelector
}
