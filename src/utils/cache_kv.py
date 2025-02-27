from ..db_drivers.kv_driver.KeyValueDriver import KeyValueDriver, KeyValueDriverConfig
from ..db_drivers.kv_driver.utils import KeyValueDBInstance, KVDBConnectionConfig

from typing import List, Union, Tuple
import pickle
import hashlib

DEFAULT_CACHEKV_CONFIG = KeyValueDriverConfig(
    db_vendor='mongo',
    db_config=KVDBConnectionConfig(
        db_info={'db': 'personalaidb_results_cache', 'table': 'personalaitable_results_cache'},
        host='localhost', port=27018, params={'username': 'user', 'password': 'pass', 'max_storage': -1},
        need_to_clear=False))

class CacheKV:
    def __init__(self, kvdriver_config: KeyValueDriverConfig = DEFAULT_CACHEKV_CONFIG):
        self.kv_conn = KeyValueDriver.connect(kvdriver_config)

    @staticmethod
    def prepare_key(key: List[object] = None, key_hash: str = None) -> str:
        # либо key- либо key_hash-значение должно быть указано,
        # инчае ошибка.
        if key is not None:
            if not CacheKV.is_key_valid(key):
                raise ValueError

            key_hash = CacheKV.get_hash(key)
        elif key_hash is not None:
            pass
        else:
            raise ValueError

        return key_hash

    @staticmethod
    def get_hash(key: List[object]) -> str:
        if not CacheKV.is_key_valid(key):
            raise ValueError

        dumps = list(map(lambda key_part: pickle.dumps(key_part), key))
        hashes = list(map(lambda dump: hashlib.sha1(dump).hexdigest(), dumps))
        concated_hashes = ''.join(hashes)
        key_hash = hashlib.sha1(concated_hashes.encode()).hexdigest()
        return key_hash

    @staticmethod
    def is_key_valid(key: List[object]) -> bool:
        return len(key) > 0

    def load_value(self, key: List[object] = None, key_hash: str = None) -> Tuple[int, Union[str, object]]:
        key_hash = CacheKV.prepare_key(key, key_hash)

        output = self.kv_conn.read([key_hash])
        filtered_output = list(filter(lambda item: item is not None, output))

        if len(filtered_output) < 1:
            return (-1, key_hash)

        raw_value = filtered_output[0].value
        formated_value = pickle.loads(raw_value)
        return (0, formated_value)

    def save_value(self, value: object, key: List[object] = None, key_hash: str = None) -> str:
        key_hash = CacheKV.prepare_key(key, key_hash)
        if self.kv_conn.item_exist(key_hash):
            raise ValueError

        new_item = KeyValueDBInstance(id=key_hash, value=pickle.dumps(value))
        self.kv_conn.create([new_item])
        return key_hash

    def check_key_exist(self, key: List[object] = None, key_hash: str = None) -> bool:
        key_hash = CacheKV.prepare_key(key, key_hash)
        return self.kv_conn.item_exist(key_hash)
