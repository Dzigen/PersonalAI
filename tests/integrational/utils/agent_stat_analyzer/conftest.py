import pytest
import sys
from typing import Dict
# TO CHANGE
PROJECT_BASE_DIR = '../'
TEST_VOLUME_DIR = './volumes'
sys.path.insert(0, PROJECT_BASE_DIR)

from src.utils.agent_stat_analyzer import AgentStatAnalyzer

from .available_agentstatanalyzer_configs import *

@pytest.fixture(scope='package')
def available_agentstats(available_agentstatanalyzer_configs):
    agentstats: Dict[str, AgentStatAnalyzer] = dict()
    for vendor, config in available_agentstatanalyzer_configs.items():
        agentstats[vendor] = AgentStatAnalyzer(config)
        agentstats[vendor].open_connections()
    return agentstats

@pytest.fixture(scope='function')
def agentstat_conn(available_agentstats, request):
    return available_agentstats[request.param]
