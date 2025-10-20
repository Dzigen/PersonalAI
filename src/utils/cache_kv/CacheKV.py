from typing import List, Union, Tuple
from typing import Tuple
import hashlib
import pickle

from .config import DEFAULT_CACHEKV_CONFIG
from ...db_drivers.kv_driver import KeyValueDriver, KeyValueDriverConfig, KeyValueDBInstance
from ...db_drivers.kv_driver.utils import AbstractKVDatabaseConnection


class CacheKV:
    kv_conn: AbstractKVDatabaseConnection

    def __init__(self, kvdriver_config: KeyValueDriverConfig = DEFAULT_CACHEKV_CONFIG):
        self.kv_conn = KeyValueDriver.connect(kvdriver_config)

    def __del__(self):
        self.kv_conn.close_connection()

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
    def get_hash(key: List[str]) -> str:
        if not CacheKV.is_key_valid(key):
            raise ValueError

        hashes = list(map(lambda k: hashlib.sha1(k.encode()).hexdigest(), key))
        concated_hashes = ''.join(hashes)
        key_hash = hashlib.sha1(concated_hashes.encode()).hexdigest()
        return key_hash

    @staticmethod
    def is_key_valid(key: List[str]) -> bool:
        return len(key) > 0

    def load_value(self, key: Union[None, List[str]] = None, key_hash: Union[None, str] = None) -> Tuple[int, str, Union[str, object]]:
        key_hash = CacheKV.prepare_key(key, key_hash)

        output = self.kv_conn.read([key_hash])
        filtered_output = list(filter(lambda item: item is not None, output))

        if len(filtered_output) < 1:
            return (-1, key_hash, None)

        raw_value = filtered_output[0].value
        formated_value = pickle.loads(raw_value)
        return (0, key_hash, formated_value)

    def save_value(self, value: object, key: Union[None, List[str]] = None, key_hash: Union[None, str] = None) -> str:
        key_hash = CacheKV.prepare_key(key, key_hash)
        if self.kv_conn.item_exist(key_hash):
            raise ValueError

        new_item = KeyValueDBInstance(id=key_hash, value=pickle.dumps(value))
        self.kv_conn.create([new_item])
        return key_hash

    def check_key_exist(self, key: List[object] = None, key_hash: str = None) -> bool:
        key_hash = CacheKV.prepare_key(key, key_hash)
        return self.kv_conn.item_exist(key_hash)

    def count_items(self) -> int:
        return self.kv_conn.count_items()

    def clear(self) -> None:
        self.kv_conn.clear()
