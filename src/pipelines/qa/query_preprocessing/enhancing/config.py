from .agent_tasks.query_expanstion import AgentQueryExpansionCheckConfigSelector
from .agent_tasks.terms_check import AgentQueryTermsCheckConfigSelector
from .agent_tasks.linguist_check import AgentQueryLinguistCheckConfigSelector

QE_MAIN_LOG_PATH = "log/qa/query_preprocessing/enhancing/main"

DEFAULT_QEXPAN_TASK_CONFIG = AgentQueryExpansionCheckConfigSelector.select(
    base_config_version='v1')
DEFAULT_TCHECK_TASK_CONFIG = AgentQueryTermsCheckConfigSelector.select(
    base_config_version='v1')
DEFAULT_LCHECK_TASK_CONFIG = AgentQueryLinguistCheckConfigSelector.select(
    base_config_version='v1')
