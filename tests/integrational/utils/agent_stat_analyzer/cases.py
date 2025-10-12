from typing import List, Dict, Tuple
import sys
import numpy as np
sys.path.insert(0, "../")

from src.utils.agent_stat_analyzer.utils import LLMInferenceStat

# 'inmemory_table', 'mongo', 'sqlite3', 'postgresql', 'mysql'
AVAILABLE_TABLE_DBS = ['inmemory_table', 'mongo', 'sqlite3', 'postgresql', 'mysql']

def prepare_test_stat(values: List[Tuple[int, float]]) -> Dict:
    not_null_values = [val for val in values if val is not None]
    return {
        'count': len(values), 'count_not_null': len(not_null_values),
        'min': round(np.min(not_null_values), 3) if len(not_null_values) > 0 else None,
        'max': round(np.max(not_null_values), 3) if len(not_null_values) > 0 else None,
        'median': round(np.median(not_null_values), 3) if len(not_null_values) > 0 else None,
        'mean': round(np.mean(not_null_values), 3) if len(not_null_values) > 0 else None,
        'std': round(np.std(not_null_values), 3) if len(not_null_values) > 0 else None,
        'sum': round(sum(not_null_values), 3) if len(not_null_values) > 0 else None
    }

#
RAW_INSTANCES1_COUNT = 0
RAW_CREATE_INSTANCES1 = {
    'prompt_tokens_amount': [],
    'generated_tokens_amount': [],
    'preparation_elapsed_time': [],
    'inference_elapsed_time': [],
}
CREATE_INSTANCES1 = [
    LLMInferenceStat(**{key: RAW_CREATE_INSTANCES1[key][i] for key in RAW_CREATE_INSTANCES1.keys()}) for i in range(RAW_INSTANCES1_COUNT)
]
EXPECTED_OUTPUT1 = {
    k: prepare_test_stat(values) for k, values in RAW_CREATE_INSTANCES1.items()
}

#
RAW_INSTANCES2_COUNT = 6
RAW_CREATE_INSTANCES2 = {
    'prompt_tokens_amount': [1,None,3,4,5,6],
    'generated_tokens_amount': [7,8,9,None,11,12],
    'preparation_elapsed_time': [0.5,1.0,None,2.0,2.5,3.0],
    'inference_elapsed_time': [3.5,4.0,4.5,5.0,None,7.0],
}
CREATE_INSTANCES2 = [
    LLMInferenceStat(**{key: RAW_CREATE_INSTANCES2[key][i] for key in RAW_CREATE_INSTANCES2.keys()}) for i in range(RAW_INSTANCES2_COUNT)
]
EXPECTED_OUTPUT2 = {
    k: prepare_test_stat(values) for k, values in RAW_CREATE_INSTANCES2.items()
}

#
RAW_INSTANCES3_COUNT = 6
RAW_CREATE_INSTANCES3 = {
    'prompt_tokens_amount': [1,2,3,4,5,6],
    'generated_tokens_amount': [7,8,9,10,11,12],
    'preparation_elapsed_time': [0.5,1.0,1.5,2.0,2.5,3.0],
    'inference_elapsed_time': [3.5,4.0,4.5,5.0,6.5,7.0],
}
CREATE_INSTANCES3 = [
    LLMInferenceStat(**{key: RAW_CREATE_INSTANCES3[key][i] for key in RAW_CREATE_INSTANCES3.keys()}) for i in range(RAW_INSTANCES3_COUNT)
]
EXPECTED_OUTPUT3 = {
    k: prepare_test_stat(values) for k, values in RAW_CREATE_INSTANCES3.items()
}


# instances, expected
ASTATANALYZ_CALC_TEST_CASES = [
    # 1. бд пустая
    [CREATE_INSTANCES1, EXPECTED_OUTPUT1],
    # 2. в бд есть строки с null-элементами
    [CREATE_INSTANCES2, EXPECTED_OUTPUT2],
    # 3. в бд есть нет строк с null-элементами
    [CREATE_INSTANCES3, EXPECTED_OUTPUT3],
]

ASTATANALYZ_POPULATED_CALC_TEST_CASES = []
for db_vendor in AVAILABLE_TABLE_DBS:
    for i in range(len(ASTATANALYZ_CALC_TEST_CASES)):
        ASTATANALYZ_POPULATED_CALC_TEST_CASES.append(
            ASTATANALYZ_CALC_TEST_CASES[i] + [db_vendor])
