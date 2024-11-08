import sys
sys.path.insert(0, "../../../")
from src.db_drivers.kv_driver import KeyValueDBInstance
from src.utils.errors import ReturnInfo

FULL_INSTANCE1 = KeyValueDBInstance(id='123', metadata={'k1': 'v1'})
FULL_INSTANCE2 = KeyValueDBInstance(id='456', metadata={'k2': 'v2'})
INSTANCE_WITH_EMPTY_METADATA = KeyValueDBInstance(id='789', metadata=dict())

INSTANCE_WITH_BAD_ID1 = KeyValueDBInstance(id=123, metadata={'k1': 'v2'})
INSTANCE_WITH_BAD_ID2 = KeyValueDBInstance(id=True, metadata={'k1': 'v2'})
INSTANCE_WITH_BAD_ID3 = KeyValueDBInstance(id=None, metadata={'k1': 'v2'})


KVDB_CREAT_TEST_CASES = [
    # пустой список
    ([[]], {'exception': False, 'db_size': 0}),
    # элемент с метаданными
    ([[FULL_INSTANCE1]], {'exception': False, 'db_size': 1}),
    # элемент без метаданныйх (пустой)
    ([[INSTANCE_WITH_EMPTY_METADATA]], {'exception': True, 'db_size': 0}),
    # несколько элементов
    ([[FULL_INSTANCE1, FULL_INSTANCE2]], {'exception': False, 'db_size': 2}),
    # дубликаты в списке
    ([[FULL_INSTANCE1, FULL_INSTANCE1]], {'exception': True, 'db_size': 0}),
    # элемент существует в бд (по id)
    ([[FULL_INSTANCE1], [FULL_INSTANCE1]], {'exception': False, 'db_size': 1}),
    # неверный формат идентификатора # 1
    ([[INSTANCE_WITH_BAD_ID1]], {'exception': True, 'db_size': 0}),
    # неверный формат идентификатора # 2
    ([[INSTANCE_WITH_BAD_ID2]], {'exception': True, 'db_size': 0}),
    # неверный формат идентификатора # 3
    ([[INSTANCE_WITH_BAD_ID3]], {'exception': True, 'db_size': 0}),
]

KVDB_DELETE_TEST_CASES = [
    # пустой список
    ([FULL_INSTANCE1, FULL_INSTANCE1], [], {'exception': False, 'db_size': 2})
    # удаление одного существующего элемента
    ([FULL_INSTANCE1, FULL_INSTANCE2], ['456'], {'exception': False, 'db_size': 1})
    # удаление одного несуществующего элемента
    ([FULL_INSTANCE1, FULL_INSTANCE2], ['789'], {'exception': False, 'db_size': 2})
    # в списке элементов на удаление есть несуществующие
    ([FULL_INSTANCE1, FULL_INSTANCE2], ['456','789'], {'exception': False, 'db_size': 1})
    # в списке элементов на удаление все существуют
    ([FULL_INSTANCE1, FULL_INSTANCE2], ['123','456'], {'exception': False, 'db_size': 0})
    #неверный формат идентификаторов 1
    ([FULL_INSTANCE1, FULL_INSTANCE2], [123], {'exception': True, 'db_size': 2})
    # неверный формат идентификатора 2
    ([FULL_INSTANCE1, FULL_INSTANCE2], [True], {'exception': True, 'db_size': 2})
    # неверный формат идентификатора 3
    ([FULL_INSTANCE1, FULL_INSTANCE2], [None], {'exception': True, 'db_size': 2})
]

KVDB_READ_TEST_CASES = [
    # пустой список
    # один существующий элемент
    # один несуществующий элемент
    # несколько существующих элементов
    # в списке есть несуществующий элемент
    # неверный формат идентификатора 1
    # неверный формат идентификатора 2
    # неверный формат идентификатора 3
]

KVDB_COUNT_TEST_CASES = [
    # нуль элементов
    # один Элемент
    # несколько элементов
]

KVDB_EXIST_TEST_CASES = [
    # элемент существует
    # элемента не существует
    # неверный формат идентификатора # 1
    # неверный формат идентификатора # 2
    # неверный формат идентификатора # 3
]

KVDB_CLEAR_TEST_CASES = [
    # чистка пустой бд
    # чиста бд с одним элементов
    # чиста бд с несколькими элементами
]
