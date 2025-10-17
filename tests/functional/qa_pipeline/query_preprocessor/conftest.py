import sys
import pytest
# TO CHANGE
PROJECT_BASE_DIR = '../'
TEST_VOLUME_DIR = './volumes'
sys.path.insert(0, PROJECT_BASE_DIR)

from src.db_drivers.kv_driver import KeyValueDriverConfig, KVDBConnectionConfig
from src.utils.agent_stat_analyzer import AgentStatAnalyzerConfig
from src.utils.agent_stat_analyzer.configs import CREATE_TABLE_SQLQUERY
from src.utils.agent_stat_analyzer.utils import LLMInferenceStat
from src.db_drivers.table_driver import TableDriverConfig, TableDBConnectionConfig
from src.agents import AgentDriverConfig, AgentDriver
from src.agents.utils import AgentConnectorConfig

KV_CACHE_CONFIG = KeyValueDriverConfig(
    db_vendor='mixed_kv',
    db_config=KVDBConnectionConfig(
        need_to_clear=False,
        params={
            'mongo_config': KVDBConnectionConfig(
                host='localhost', port=27010,
                db_info={'db': 'memorize_db', 'table': None},
                params={'username': 'user',
                        'password': 'pass', 'max_storage': -1},
                need_to_clear=False
            ),
            'redis_config': KVDBConnectionConfig(
                host='localhost', port=6370,
                db_info={'db': 0, 'table': None},
                params={'ss_name': 'sorted_node_pairs',
                        'hs_name': 'node_pairs', 'max_storage': 50000000},
                need_to_clear=False
            )
        }
    )
)

INFSTAT_CONFIG = AgentStatAnalyzerConfig(
    table_driver_config=TableDriverConfig(
        db_vendor='sqlite3',
        db_config=TableDBConnectionConfig(
            db_info={
                'db': 'test_llmstatdb', 'table': 'test_llmstattable',
                'table_info': LLMInferenceStat,
                'create_table_query': CREATE_TABLE_SQLQUERY
            },
            params={
                'database_path': f'{TEST_VOLUME_DIR}/sqlite3'
            },
            need_to_clear=False
        )
    )
)

@pytest.fixture(scope='package')
def agent_conn():

    config = AgentDriverConfig(
        name='ollama',
        agent_config=AgentConnectorConfig(
            gen_strategy={"num_predict": 2048, "seed": 42, "top_k": 1, "temperature": 0.0},
            credentials={"model": 'llama3.1:8b', "host": 'localhost', "port": 11437},
            ext_params={"timeout": 560, "keep_alive": -1}))

    return AgentDriver.connect(config)
