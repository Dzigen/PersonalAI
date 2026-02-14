from typing import List, Union, Tuple
import hashlib
import pickle

from .config import DEFAULT_CACHEKV_CONFIG
from ...db_drivers.kv_driver import KeyValueDriver, KeyValueDriverConfig, KeyValueDBInstance
from ...db_drivers.kv_driver.utils import AbstractKVDatabaseConnection


class CacheKV:
    kv_conn: AbstractKVDatabaseConnection

    def __init__(self, kvdriver_config: KeyValueDriverConfig = DEFAULT_CACHEKV_CONFIG):
        self.kv_conn = KeyValueDriver.connect(kvdriver_config)

    def close_connection(self):
        # print("closing kv-cache conn")
        self.kv_conn.close_connection()

    @staticmethod
    def prepare_key(key: List[object] = None, key_hash: str = None) -> str:
        """Метод предназначен для подготовки хеш-ключа для обращения к кешу.

        :param key: Набор на основе которого будет вычислен хеш-ключ. Значение по умолчанию None.
        :type key: List[object]
        :param key_hash: Уже готовый хеш-ключ, если он был вычислен заранее. Значение по умолчанию None.
        :type key_hash: str
        :return: Строковый хеш-ключ для обращения к кешу.
        :rtype: str
        """
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
        """Метод предназначен для получения детерминированного хеш-ключа на основе списка строк.

        :param key: Список строк, на основе которого будет вычислен хеш-ключ.
        :type key: List[str]
        :return: Строковый хеш (SHA1) от конкатенированных хешей элементов key.
        :rtype: str
        """
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
        """Загружает значение из key-value-хранилища по ключу или хеш-ключу.

        :param key: Набор на основе которого будет вычислен хеш. Значение по умолчанию None.
        :type key: Union[None, List[str]]
        :param key_hash: Уже готовый хеш-ключ, если он был вычислен заранее. Значение по умолчанию None.
        :type key_hash: Union[None, str]
        :return: Кортеж из трёх элементов: (1) статус операции: 0 — значение найдено, -1 — значение отсутствует; (2) использованный хеш-ключ; (3) загруженное значение или None, если значение не найдено.
        :rtype: Tuple[int, str, Union[str, object]]
        """
        key_hash = CacheKV.prepare_key(key, key_hash)

        output = self.kv_conn.read([key_hash])
        filtered_output = list(filter(lambda item: item is not None, output))

        if len(filtered_output) < 1:
            return (-1, key_hash, None)

        raw_value = filtered_output[0].value
        formated_value = pickle.loads(raw_value)
        return (0, key_hash, formated_value)

    def save_value(self, value: object, key: Union[None, List[str]] = None, key_hash: Union[None, str] = None) -> str:
        """Сохраняет значение в key-value-хранилище по ключу или хеш-ключу.

        :param value: Сохраняемое значение.
        :type value: object
        :param key: Набор на основе которого будет вычислен хеш. Значение по умолчанию None.
        :type key: Union[None, List[str]]
        :param key_hash: Уже готовый хеш-ключ, если он был вычислен заранее. Значение по умолчанию None.
        :type key_hash: Union[None, str]
        :return: Использованный хеш-ключ, под которому сохранено значение.
        :rtype: str
        """
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
