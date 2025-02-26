from ..db_drivers.kv_driver.KeyValueDriver import KeyValueDriver, KeyValueDriverConfig
from ..db_drivers.kv_driver.utils import KeyValueDBInstance, KVDBConnectionConfig

from typing import List, Union
import pickle
import hashlib

DEFAULT_CACHEKV_CONFIG = KeyValueDriverConfig(
    db_vendor='mongo',
    db_config=KVDBConnectionConfig(
        db_info={'db': 'personalaidb_results_cache', 'table': 'personalaitable_results_cache'},
        host='localhost', port=27018, params={'username': 'user', 'password': 'pass', 'max_storage': -1},
        need_to_clear=False))

class CacheKV:

    def __init__(self, kvdriver_config: KeyValueDriverConfig):
        self.kv_conn = KeyValueDriver.connect(kvdriver_config)

    def get_hash(self, key: List[object]) -> str:
        if not self.is_key_valid(key):
            raise ValueError

        dumps = list(map(lambda key_part: pickle.dumps(key_part), key))
        hashes = list(map(lambda dump: hashlib.sha1(dump).hexdigest(), dumps))
        concated_hashes = ''.join(hashes)
        key_hash = hashlib.sha1(concated_hashes.encode()).hexdigest()
        return key_hash

    def is_key_valid(self, key: List[object]) -> bool:
        return len(key) > 0

    def load_value(self, key: List[object]) -> object:
        if not self.is_key_valid(key):
            raise ValueError

        key_hash = self.get_hash(key)
        output = self.kv_conn.read([key_hash])

        if len(output) < 1:
            return None

        raw_value = output[0].value
        formated_value = pickle.loads(raw_value)
        return formated_value

    def save_value(self, key: List[object], value: object) -> None:
        if not self.is_key_valid(key):
            raise ValueError

        key_hash = self.get_hash(key)
        new_item = KeyValueDBInstance(id=key_hash, value=pickle.dumps(value))
        self.kv_conn.create([new_item])
