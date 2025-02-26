from .agent_tasks.thesis_extraction import AgentThesisExtrTaskConfigSelector
from .agent_tasks.triplet_extraction import AgentTripletExtrTaskConfigSelector

MEM_EXTRACTOR_MAIN_LOG_PATH = "log/memorize/extractor/main"
DEFAULT_TRIPLETS_EXTR_TASK_CONFIG =  AgentTripletExtrTaskConfigSelector.select(base_config_version='v1')
DEFAULT_THESISES_EXTR_TASK_CONFIG =  AgentThesisExtrTaskConfigSelector.select(base_config_version='v1')
