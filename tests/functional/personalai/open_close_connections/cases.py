
from ..cases import AVAILABLE_PAICONFIG_COMBINATIONS, \
    AVAILABLE_CACHE_DBS, AVAILABLE_AGENTSTAT_DBS

LANG = 'auto'

# open_num, pai_config, cache_kvdriver_config, inferencestat_config
OPENCONNECTIONS_TEST_CASES = [
    # соединение уже установлено
    # успешная установка соединения сразу после инициализации PersonalAI-класса
    0, 1, 2
]

POPULATED_OPENCONNECTIONS_TEST_CASES = []
for case in OPENCONNECTIONS_TEST_CASES:
    for pai_vendors in AVAILABLE_PAICONFIG_COMBINATIONS:
        pai_kw = "/".join(pai_vendors)
        for cache_vendor in AVAILABLE_CACHE_DBS:
            for agentstat_vendor in AVAILABLE_AGENTSTAT_DBS:
                POPULATED_OPENCONNECTIONS_TEST_CASES.append(
                    [case, pai_kw, cache_vendor, agentstat_vendor])


# ============================

# close_num, pai_config, cache_kvdriver_config, inferencestat_config
CLOSECONNECTIONS_TEST_CASES = [
    # обрыв соединения сразу после инициализации PersonalAI-класса + успешный обрыв соединения + соединение уже закрыто
    0, 1, 2
]

POPULATED_CLOSECONNECTIONS_TEST_CASES = []
for case in CLOSECONNECTIONS_TEST_CASES:
    for pai_vendors in AVAILABLE_PAICONFIG_COMBINATIONS:
        pai_kw = "/".join(pai_vendors)
        for cache_vendor in AVAILABLE_CACHE_DBS:
            for agentstat_vendor in AVAILABLE_AGENTSTAT_DBS:
                POPULATED_CLOSECONNECTIONS_TEST_CASES.append(
                    [case, pai_kw, cache_vendor, agentstat_vendor])

# openclose_num, pai_config, cache_kvdriver_config, inferencestat_config
CLOSETHENOPENCONNECTIONS_TEST_CASES = [
    # повторная установка соединения после его обрыва 
    0, 1, 2
]

POPULATED_CLOSETHENOPENCONNECTIONS_TEST_CASES = []
for case in CLOSETHENOPENCONNECTIONS_TEST_CASES:
    for pai_vendors in AVAILABLE_PAICONFIG_COMBINATIONS:
        pai_kw = "/".join(pai_vendors)
        for cache_vendor in AVAILABLE_CACHE_DBS:
            for agentstat_vendor in AVAILABLE_AGENTSTAT_DBS:
                POPULATED_CLOSETHENOPENCONNECTIONS_TEST_CASES.append(
                    [case, pai_kw, cache_vendor, agentstat_vendor])
