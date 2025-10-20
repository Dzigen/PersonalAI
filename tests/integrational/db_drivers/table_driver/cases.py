import sys
sys.path.insert(0, "../")

from src.db_drivers.table_driver import TableDBInstance
from src.utils.agent_stat_analyzer.utils import LLMInferenceStat

# TO CHANGE
# 'inmemory_table', 'mongo', 'sqlite3', 'postgresql', 'mysql'
AVAILABLE_TABLE_DBS = ['inmemory_table', 'mongo', 'sqlite3', 'postgresql', 'mysql']

###############################################################################################

STAT_VALUES1 = LLMInferenceStat(
    prompt_tokens_amount=10, generated_tokens_amount=20, inference_elapsed_time=10)
STAT_VALUES2 = LLMInferenceStat(
    prompt_tokens_amount=10, generated_tokens_amount=20, inference_elapsed_time=10)
STAT_VALUES3 = LLMInferenceStat(
    prompt_tokens_amount=10, generated_tokens_amount=20, inference_elapsed_time=10)

INSTANCE1 = TableDBInstance(id='1', values=STAT_VALUES1)
INSTANCE1_2 = TableDBInstance(id='2', values=STAT_VALUES1)
INSTANCE2 = TableDBInstance(id='3', values=STAT_VALUES2)
INSTANCE2_2 = TableDBInstance(id='4', values=STAT_VALUES2)
INSTANCE3 = TableDBInstance(id='5', values=STAT_VALUES3)
INSTANCE3_2 = TableDBInstance(id=None, values=STAT_VALUES3)

INSTANCE_W_BAD_ID1 = TableDBInstance(id=False, values=STAT_VALUES1)


###############################################################################################

TABLEDB_CREATE_TEST_CASES = [
    # 1. пустой список
    [[[]], {'exception': False, 'db_size': 0}],
    # 2. несколько элементов
    [[[INSTANCE1, INSTANCE2]], {'exception': False, 'db_size': 2}],
    # 3. дубликаты в списке
    [[[INSTANCE1, INSTANCE1]], {'exception': True, 'db_size': 0}],
    # 4. элемент существует в бд (по id)
    [[[INSTANCE1], [INSTANCE1]], {'exception': False, 'db_size': 1}],
    # 6. неверный формат идентификатора # 1
    [[[INSTANCE_W_BAD_ID1]], {'exception': True, 'db_size': 0}],
    # 7. Пустое id-поле
    [[[INSTANCE3_2]], {'exception': False, 'db_size': 1}]
]

TABLEDB_POPULATED_CREATE_TEST_CASES = []
for db_vendor in AVAILABLE_TABLE_DBS:
    for i in range(len(TABLEDB_CREATE_TEST_CASES)):
        TABLEDB_POPULATED_CREATE_TEST_CASES.append(
            TABLEDB_CREATE_TEST_CASES[i] + [db_vendor])

###############################################################################################

TABLEDB_DELETE_TEST_CASES = [
    # 1. пустой список
    [[INSTANCE1, INSTANCE2], [], {'exception': False, 'db_size': 2}],
    # 2. удаление одного существующего элемента
    [[INSTANCE1, INSTANCE2, INSTANCE3], ['3'],
        {'exception': False, 'db_size': 2}],
    # 3. удаление одного несуществующего элемента
    [[INSTANCE1, INSTANCE2], ['9345'],
        {'exception': False, 'db_size': 2}],
    # 4. в списке элементов на удаление есть несуществующие
    [[INSTANCE1, INSTANCE2, INSTANCE3, INSTANCE1_2], ['1', '3', '9245'],
        {'exception': False, 'db_size': 2}],
    # 5. в списке элементов на удаление все существуют
    [[INSTANCE1, INSTANCE2], ['1', '3'],
        {'exception': False, 'db_size': 0}],
    # 6. неверный формат идентификатора 1
    [[INSTANCE1, INSTANCE2], [True],
        {'exception': True, 'db_size': 2}],
    # 7. неверный формат идентификатора 2
    [[INSTANCE1, INSTANCE2], [None],
        {'exception': True, 'db_size': 2}]
]

TABLEDB_POPULATED_DELETE_TEST_CASES = []
for db_vendor in AVAILABLE_TABLE_DBS:
    for i in range(len(TABLEDB_DELETE_TEST_CASES)):
        TABLEDB_POPULATED_DELETE_TEST_CASES.append(
            TABLEDB_DELETE_TEST_CASES[i] + [db_vendor])

###############################################################################################

TABLEDB_READ_TEST_CASES = [
    # 1. пустой список
    [[INSTANCE1, INSTANCE2, INSTANCE2_2], [], {
        'exception': False, 'output_ids': []}],
    # 2. один существующий элемент
    [[INSTANCE1, INSTANCE2], ['1'], {
        'exception': False, 'output_ids': ['1']}],
    # 3. один несуществующий элемент
    [[INSTANCE1, INSTANCE2], ['925'], {
        'exception': False, 'output_ids': [None]}],
    # 4. несколько существующих элементов
    [[INSTANCE1, INSTANCE2], ['1', '3'], {
        'exception': False, 'output_ids': ['1', '3']}],
    # 5. в списке есть несуществующий элемент
    [[INSTANCE1, INSTANCE2, INSTANCE3], ['1', '9243', '3'], {
        'exception': False, 'output_ids': ['1', None, '3']}],
    # 6. неверный формат идентификатора 2
    [[INSTANCE1, INSTANCE2], [True],
        {'exception': True, 'output_ids': []}],
    # 7. неверный формат идентификатора 3
    [[INSTANCE1, INSTANCE2], [None],
        {'exception': True, 'output_ids': []}]
]

TABLEDB_POPULATED_READ_TEST_CASES = []
for db_vendor in AVAILABLE_TABLE_DBS:
    for i in range(len(TABLEDB_READ_TEST_CASES)):
        TABLEDB_POPULATED_READ_TEST_CASES.append(
            TABLEDB_READ_TEST_CASES[i] + [db_vendor])

###############################################################################################

TABLEDB_COUNT_TEST_CASES = [
    # 1. нуль элементов
    [[], 0],
    # 2. один Элемент
    [[INSTANCE1], 1],
    # 3. несколько элементов
    [[INSTANCE1, INSTANCE2, INSTANCE3, INSTANCE3_2], 4]
]

TABLEDB_POPULATED_COUNT_TEST_CASES = []
for db_vendor in AVAILABLE_TABLE_DBS:
    for i in range(len(TABLEDB_COUNT_TEST_CASES)):
        TABLEDB_POPULATED_COUNT_TEST_CASES.append(
            TABLEDB_COUNT_TEST_CASES[i] + [db_vendor])

###############################################################################################

TABLEDB_EXIST_TEST_CASES = [
    # 1. элемент существует
    [[INSTANCE1, INSTANCE2], '1',
        {'exception': False, 'exist': True}],
    # 2. элемента не существует
    [[INSTANCE1, INSTANCE2], '9245',
        {'exception': False, 'exist': False}],
    # 3. неверный формат идентификатора # 1
    [[INSTANCE1, INSTANCE2], 1, {
        'exception': True, 'exist': False}],
    # 4. неверный формат идентификатора # 2
    [[INSTANCE1, INSTANCE2], True,
        {'exception': True, 'exist': False}],
    # 5. неверный формат идентификатора # 3
    [[INSTANCE1, INSTANCE2], None,
        {'exception': True, 'exist': False}]
]

TABLEDB_POPULATED_EXIST_TEST_CASES = []
for db_vendor in AVAILABLE_TABLE_DBS:
    for i in range(len(TABLEDB_EXIST_TEST_CASES)):
        TABLEDB_POPULATED_EXIST_TEST_CASES.append(
            TABLEDB_EXIST_TEST_CASES[i] + [db_vendor])

###############################################################################################

TABLEDB_CLEAR_TEST_CASES = [
    # 1. чистка пустой бд
    [[]],
    # 2. чиста бд с одним элементов
    [[INSTANCE1]],
    # 3. чиста бд с несколькими элементами
    [[INSTANCE1, INSTANCE2, INSTANCE3]]
]

TABLEDB_POPULATED_CLEAR_TEST_CASES = []
for db_vendor in AVAILABLE_TABLE_DBS:
    for i in range(len(TABLEDB_CLEAR_TEST_CASES)):
        TABLEDB_POPULATED_CLEAR_TEST_CASES.append(
            TABLEDB_CLEAR_TEST_CASES[i] + [db_vendor])
