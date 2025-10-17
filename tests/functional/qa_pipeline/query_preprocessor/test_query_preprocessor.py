import pytest
from typing import List, Dict
from tqdm import tqdm
import sys
import flatdict

# TO CHANGE
PROJECT_BASE_DIR = '../'
sys.path.insert(0, PROJECT_BASE_DIR)

from src.pipelines.qa.query_preprocessing import QueryPreprocessor, QueryPreprocessorConfig
from src.agents.utils import AbstractAgentConnector
from .cases import QP_POPULATED_TEST_CASES
from .conftest import KV_CACHE_CONFIG, INFSTAT_CONFIG

@pytest.mark.parametrize("query, qp_config, agent_conn", QP_POPULATED_TEST_CASES, indirect=['agent_conn'])
def test_query_preprocessor(query: str, qp_config: QueryPreprocessorConfig, agent_conn: AbstractAgentConnector):

    qp_stage = QueryPreprocessor(
        agent_conn,
        config=qp_config,
        cache_kvdriver_config=KV_CACHE_CONFIG,
        inferencestat_config=INFSTAT_CONFIG)

    qp_stage.clear_agent_tgen_stat()
    qp_stage.clear_kv_caches()

    _, info = qp_stage.perform(query)
    assert info.status.value == 0

    qp_stage.clear_agent_tgen_stat()
    qp_stage.clear_kv_caches()
