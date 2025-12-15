from ....utils import AgentTaskSolverConfig
from src.utils import Logger
from src.dialogue_processing.utils import BaseAgentTaskConfigSelector
from .general_parsers import rephrase_chunk_custom_formate, rephrase_chunk_custom_postprocess
from .v1 import REPH_CHUNK_SUITE_V1

REPH_CHUNK_LOG_PATH = "log/dialogue_processing/chunk_rephraser/agent_tasks/chunk_rephraser"

AVAILABLE_REPH_CHUNK_TCONFIGS = {
    'v1': REPH_CHUNK_SUITE_V1,
}


class AgentRephChunkTaskConfigSelector(BaseAgentTaskConfigSelector):
    @staticmethod
    def get_available_configs():
        return AVAILABLE_REPH_CHUNK_TCONFIGS

    @staticmethod
    def select(base_config_version: str = 'v1',
               cache_table_name: str = "rephrase_chunk_agent_task_cache",
               inferencestat_table_name: str = "rephrase_chunk_agent_task_stat") -> AgentTaskSolverConfig:
        return AgentTaskSolverConfig(
            version=base_config_version,
            suites=AVAILABLE_REPH_CHUNK_TCONFIGS[base_config_version],
            formate_context_func=rephrase_chunk_custom_formate, postprocess_answer_func=rephrase_chunk_custom_postprocess,
            cache_table_name=cache_table_name,
            inferencestat_table_name=inferencestat_table_name,
            log=Logger(REPH_CHUNK_LOG_PATH))
