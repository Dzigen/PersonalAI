import sys
import joblib

# TO CHANGE
BASEDIR = "../../"
sys.path.insert(0, BASEDIR)

from src.pipelines.qa.knowledge_retriever import AStarGraphSearchConfig, AStarMetricsConfig, BFSSearchConfig, MixturedGraphSearchConfig, NaiveBFSGraphSearchConfig
from src.pipelines.qa.knowledge_retriever.TripletsFilter import TripletsFilterConfig
from src.db_drivers.kv_driver import KVDBConnectionConfig, KeyValueDriverConfig
from src.db_drivers.kv_driver.connectors import DEFAULT_MIXEDKV_CONFIG
from src.utils import NodeType, Logger

# retrieve
RETRIVER_CONFIG_DUMP = "retriever_config"

# DEFAULT_MIXEDKV_CONFIG.params['redis_config'].host = 'localhost'
# DEFAULT_MIXEDKV_CONFIG.params['mongo_config'].host = 'localhost'

# KV_STORAGE_CONFIG = KeyValueDriverConfig(db_vendor='mixed_kv', db_config=DEFAULT_MIXEDKV_CONFIG)

# retriever_config= AStarGraphSearchConfig(
#     metrics_config=AStarMetricsConfig(h_metric_name='ip', kvdriver_config=KV_STORAGE_CONFIG),
#     max_depth=8, max_passed_nodes=500,
#     accepted_node_types=[NodeType.object , NodeType.hyper, NodeType.episodic]
# )

# retriever_config = BFSSearchConfig(
#      strict_filter = True,
#      hyper_num = 15,
#      episodic_num = 15,
#      chain_triplets_num = 25,
#      other_triplets_num = 6
#  )

retriever_config = NaiveBFSGraphSearchConfig(
    max_depth=5, max_width=10, max_passed_nodes=50,
    accepted_node_types=[NodeType.object , NodeType.hyper, NodeType.episodic])

joblib.dump(retriever_config, RETRIVER_CONFIG_DUMP)

# filter config
FILTER_CONFIG_DUMP = "filter_config"

filter_config = TripletsFilterConfig(
    max_k=50
)

print("retriever: ",retriever_config)
print("filter: ", filter_config)

joblib.dump(filter_config, FILTER_CONFIG_DUMP)
