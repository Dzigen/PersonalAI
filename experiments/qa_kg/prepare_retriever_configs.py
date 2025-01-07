import sys
import joblib

# TO CHANGE
BASEDIR = "../../"
sys.path.insert(0, BASEDIR)

from src.pipelines.qa.knowledge_retriever import AStarGraphSearchConfig, AStarMetricsConfig, BFSSearchConfig, MixturedGraphSearchConfig
from src.pipelines.qa.knowledge_retriever.TripletsFilter import TripletsFilterConfig

# retrieve
RETRIVER_CONFIG_DUMP = "retriever_config"

retriever_config = BFSSearchConfig(
    strict_filter=True,
    hyper_episodic_num=15,
    chain_triplets_num=25,
    other_triplets_num=6
)

joblib.dump(retriever_config, RETRIVER_CONFIG_DUMP)


# filter config
FILTER_CONFIG_DUMP = "filter_config"

filter_config = TripletsFilterConfig(
    max_k=50
)

joblib.dump(filter_config, FILTER_CONFIG_DUMP)
