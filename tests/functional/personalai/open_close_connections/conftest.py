from ..available_personalai_configs import *
from ....integrational.db_drivers.kv_driver.available_kv_configs import *
from ....integrational.utils.agent_stat_analyzer.available_agentstatanalyzer_configs import *

@pytest.fixture(scope='function')
def pai_config(available_personalai_configs, request):
    return available_personalai_configs[request.param]

@pytest.fixture(scope='function')
def cache_config(available_kv_configs, request):
    return available_kv_configs.get(request.param, None)

@pytest.fixture(scope='function')
def agentstat_config(available_agentstatanalyzer_configs, request):
    return available_agentstatanalyzer_configs.get(request.param, None)