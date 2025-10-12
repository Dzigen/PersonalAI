import pytest
from typing import List, Dict, Union
import sys
import numpy as np
from copy import deepcopy
sys.path.insert(0, "../")

from src.utils.agent_stat_analyzer.utils import LLMInferenceStat
from src.utils.agent_stat_analyzer import AgentStatAnalyzer

from .cases import ASTATANALYZ_POPULATED_CALC_TEST_CASES


@pytest.mark.parametrize("instances, expected, agentstat_conn",
                         ASTATANALYZ_POPULATED_CALC_TEST_CASES,
                         indirect=['agentstat_conn'])
def test_calculate(instances: List[LLMInferenceStat], expected: Dict[str, Dict[str, Union[None, float, int]]], agentstat_conn: AgentStatAnalyzer):
    agentstat_conn.db_conn.clear()
    assert agentstat_conn.db_conn.count_items() == 0

    instances = deepcopy(instances)

    agentstat_conn.add_values(instances)
    assert agentstat_conn.db_conn.count_items() == len(instances)

    real = agentstat_conn.calculate_stat()

    print("real: ", real)
    print("expected: ", expected)

    assert len(list(real.keys())) == len(list(expected.keys()))
    for cname in expected.keys():
        assert len(list(real[cname].keys())) == len(list(expected[cname].keys()))
        for metric in expected[cname].keys():
            if expected[cname][metric] is None:
                assert real[cname][metric] == expected[cname][metric]
            else:
                assert np.abs(real[cname][metric] - expected[cname][metric]) < 1e-5
