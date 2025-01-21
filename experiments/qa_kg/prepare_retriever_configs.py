import sys
import joblib

# TO CHANGE
BASEDIR = "../../"
sys.path.insert(0, BASEDIR)

from src.pipelines.qa.kg_reasoning.weak_reasoner.knowledge_retriever import AStarGraphSearchConfig, AStarMetricsConfig, \
    BFSSearchConfig, MixturedGraphSearchConfig, NaiveBFSGraphSearchConfig, NaiveGraphSearchConfig
from src.pipelines.qa.kg_reasoning.weak_reasoner.knowledge_retriever.TripletsFilter import TripletsFilterConfig
from src.pipelines.qa.kg_reasoning.weak_reasoner import WeakKGReasonerConfig, QueryLLMParserConfig, KnowledgeComparatorConfig, KnowledgeRetrieverConfig, QALLMGeneratorConfig

from src.db_drivers.kv_driver import KVDBConnectionConfig, KeyValueDriverConfig
from src.db_drivers.kv_driver.connectors import DEFAULT_MIXEDKV_CONFIG
from src.utils import NodeType, Logger

# retrieve

# DEFAULT_MIXEDKV_CONFIG.params['redis_config'].host = 'localhost'
# DEFAULT_MIXEDKV_CONFIG.params['mongo_config'].host = 'localhost'

# KV_STORAGE_CONFIG = KeyValueDriverConfig(db_vendor='mixed_kv', db_config=DEFAULT_MIXEDKV_CONFIG)

# astar_config= AStarGraphSearchConfig(
#     metrics_config=AStarMetricsConfig(h_metric_name='ip', kvdriver_config=KV_STORAGE_CONFIG),
#     max_depth=8, max_passed_nodes=500,
#     accepted_node_types=[NodeType.object , NodeType.hyper, NodeType.episodic]
# )

retriever1_config = BFSSearchConfig(
     strict_filter = True,
     hyper_num = 15,
     episodic_num = 15,
     chain_triplets_num = 25,
     other_triplets_num = 6
 )

retriever2_config = NaiveBFSGraphSearchConfig(
    max_depth=5, max_width=10, max_passed_nodes=50,
    accepted_node_types=[NodeType.object , NodeType.hyper, NodeType.episodic])

# retriever_name = 'mixture'
# retriever_config = MixturedGraphSearchConfig(
#     retriever1_name='bfs',
#     retriever1_config=retriever1_config,
#     retriever2_name='naive_bfs',
#     retriever2_config=retriever2_config
# )

retriever_name = 'naive_retriever'
retriever_config = NaiveGraphSearchConfig(max_k=50)

# filter config
# filter_name = 'naive'
# filter_config = TripletsFilterConfig(
#     max_k=50
# )
filter_name = None
filter_config = None

REASONER_CONFIG_DUMP = 'reasoner_config'

reasoner_config = WeakKGReasonerConfig(
    query_parser_config=None, #QueryLLMParserConfig(lang='en'),
    knowledge_comparator_config=None, #KnowledgeComparatorConfig(),
    knowledge_retriever_config=KnowledgeRetrieverConfig(
        retriever_method=retriever_name,retriever_config=retriever_config,
        filter_method=filter_name, filter_config=filter_config),
    answer_generator_config=QALLMGeneratorConfig(lang='en'))

print("retriever: ", retriever_config)
print("="*10)
print("filter: ", filter_config)
print("="*10)
print("reasoner: ", reasoner_config)

joblib.dump(reasoner_config, REASONER_CONFIG_DUMP)
