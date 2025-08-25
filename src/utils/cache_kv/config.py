from ...db_drivers.kv_driver.utils import KVDBConnectionConfig
from ...db_drivers.kv_driver.KeyValueDriver import KeyValueDriverConfig

DEFAULT_CACHEKV_CONFIG = KeyValueDriverConfig(
    db_vendor='mongo',
    db_config=KVDBConnectionConfig(
        db_info={'db': 'personalaidb_results_cache', 'table': 'personalaitable_results_cache'},
        host='localhost', port=27018, params={'username': 'user', 'password': 'pass', 'max_storage': -1},
        need_to_clear=False))
