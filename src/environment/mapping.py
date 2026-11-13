from typing import Dict

from ..utils.agent_stat_analyzer import AgentStatAnalyzerConfig
from ..db_drivers.kv_driver import KeyValueDriverConfig
from ..kg_model import KnowledgeGraphModelConfig
from ..TextIdStore import TextIdStoreConfig
from ..pipelines.qa import QAPipelineConfig
from ..pipelines.memorize import MemPipelineConfig
from ..utils.data_structs import BaseComponentConfig

KW_TO_CONFIGURATIONS_MAPPING: Dict[str, BaseComponentConfig] = {
    'kg_model_config': KnowledgeGraphModelConfig,
    'textidstore_config': TextIdStoreConfig,

    'mem_pipeline_config': MemPipelineConfig,
    'qa_pipeline_config': QAPipelineConfig,
    
    'cache_kvdriver_config': KeyValueDriverConfig,
    'inferencestat_config': AgentStatAnalyzerConfig
}