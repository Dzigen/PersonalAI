import pytest

import sys
sys.path.insert(0, "../")

from typing import List, Union

from src.main import PersonalAIConfig, AgentStatAnalyzerConfig, KeyValueDriverConfig, PersonalAI

from .cases import POPULATED_OPENCONNECTIONS_TEST_CASES, POPULATED_CLOSECONNECTIONS_TEST_CASES, \
    POPULATED_CLOSETHENOPENCONNECTIONS_TEST_CASES
from ..conftest import clear_tests_output

clear_tests_output()

@pytest.mark.parametrize(
    "open_num, pai_config, cache_config, agentstat_config", 
    POPULATED_OPENCONNECTIONS_TEST_CASES, 
    indirect=["pai_config", "cache_config", "agentstat_config"]
)
def test_open_connections(
    open_num: int, pai_config: PersonalAIConfig, cache_config: Union[KeyValueDriverConfig, None], 
    agentstat_config: Union[AgentStatAnalyzerConfig, None]):

    pai = PersonalAI(pai_config, cache_config, agentstat_config)
    assert not pai.is_connections_open(detailed=False)

    for _ in range(open_num):
        pai.open_connections()
        assert pai.is_connections_open(detailed=False)

    pai.close_connections()
    assert not pai.is_connections_open(detailed=False)

@pytest.mark.parametrize(
    "close_num, pai_config, cache_config, agentstat_config", 
    POPULATED_CLOSECONNECTIONS_TEST_CASES, 
    indirect=["pai_config", "cache_config", "agentstat_config"]
)
def test_close_connections(
    close_num: int, pai_config: PersonalAIConfig, cache_config: Union[KeyValueDriverConfig, None], 
    agentstat_config: Union[AgentStatAnalyzerConfig, None]):

    pai = PersonalAI(pai_config, cache_config, agentstat_config)
    pai.close_connections()
    assert not pai.is_connections_open(detailed=False)
    pai.open_connections()
    assert pai.is_connections_open(detailed=False)

    for _ in range(close_num):
        pai.close_connections()
        assert not pai.is_connections_open(detailed=False)

    pai.close_connections()
    assert not pai.is_connections_open(detailed=False)
            
@pytest.mark.parametrize(
    "openclose_num, pai_config, cache_config, agentstat_config", 
    POPULATED_CLOSETHENOPENCONNECTIONS_TEST_CASES, 
    indirect=["pai_config", "cache_config", "agentstat_config"]
)
# повторная установка соединения после его обрыва 
def test_close_then_open_connections(
    openclose_num: int, pai_config: PersonalAIConfig, cache_config: Union[KeyValueDriverConfig, None], 
    agentstat_config: Union[AgentStatAnalyzerConfig, None]):
    pai = PersonalAI(pai_config, cache_config, agentstat_config)
    assert not pai.is_connections_open(detailed=False)

    for _ in range(openclose_num):
        pai.open_connections()
        assert pai.is_connections_open(detailed=False)
        pai.close_connections()
        assert not pai.is_connections_open(detailed=False)
        pai.open_connections()
        assert pai.is_connections_open(detailed=False)
        pai.close_connections()
        assert not pai.is_connections_open(detailed=False)

@pytest.mark.parametrize(
    "pai_config, cache_config, agentstat_config, operations_sequence", [
    # после инициализации PersonalAI-класса все соединения закрыты
    # после обрыва соединений отсутствуют какие-либо открытые подключения
    # после открытия соединений отсутствуют закрытые соединения
    ],
    indirect=["pai_config", "cache_config", "agentstat_config"]
)
def test_is_connections_open(
    pai_config: PersonalAIConfig, cache_config: Union[KeyValueDriverConfig, None], 
    agentstat_config: Union[AgentStatAnalyzerConfig, None], operations_sequence: List[str]):
    # TODO
    raise NotImplementedError