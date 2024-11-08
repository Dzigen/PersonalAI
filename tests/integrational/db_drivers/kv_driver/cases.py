import sys
sys.path.insert(0, "../../../")
from src.db_drivers.kv_driver import KeyValueDBInstance
from src.utils.errors import ReturnInfo

KVDB_CREAT_TEST_CASES = []
KVDB_DELETE_TEST_CASES = []
KVDB_READ_TEST_CASES = []
KVDB_COUNT_TEST_CASES = []
KVDB_EXIST_TEST_CASES = []
KVDB_CLEAR_TEST_CASES = []
