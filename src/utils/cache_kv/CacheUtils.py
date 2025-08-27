from typing import Union
from copy import deepcopy

from .utils import AbstractCacheUtils
from .CacheKV import CacheKV
from ...db_drivers.kv_driver.KeyValueDriver import KeyValueDriverConfig

class CacheUtils(AbstractCacheUtils):
    def init_cachekv(self, cache_kvdriver_config: Union[KeyValueDriverConfig, None] = None, cache_table_name: Union[None,str] = None) -> Union[None, CacheKV]:
        """Метод предназначен для создания базы данных с целью кеширования требуемых результатов.

        :param cache_kvdriver_config: Конфигурация базы данных для хранения кешируемых результатов. Значение по умолчанию None.
        :type cache_kvdriver_config: Union[KeyValueDriverConfig, None]
        :param cache_table_name: Название таблицы в структуре (базе) данных, куда будут сохраняться (кешироваться) результаты. Значение по умолачанию None.
        :type cache_table_name: Union[None,str], optional
        :return: Если cache_kvdriver_config равен None, то будет возвращен None, иначе будет возвращен интерфейс взаимодействия с созданным кешем.
        :rtype: Union[None, CacheKV]
        """
        cachekv = None
        if cache_kvdriver_config is not None:
            if cache_table_name is None:
                raise ValueError
            cache_config = deepcopy(cache_kvdriver_config)
            cache_config.db_config.db_info['table'] = cache_table_name
            cachekv = CacheKV(cache_config)

        return cachekv

    def cache_method_output(function):
        """Метод является декоратором для кеширования результатов, возвращаемой от соответсвующего (декорируемого) метода.
        Реализация класса, метод которого декорируется, должена содержеать get_cache_key-метод для идентификации (генерации ключа) кешируемого результата.
        """
        def wrapper(self, *args, **kwargs):
            cached_flag = False
            cache_key = self.get_cache_key(*args, **kwargs)
            key_hash = None

            if self.cachekv is not None:
                self.log("Поиск результата в кеше...", verbose=self.verbose)
                cstatus, key_hash, cached_result = self.cachekv.load_value(key=cache_key)
                if cstatus == 0:
                    self.log("Результат по заданной конфигурации гиперпараметров уже был получен.", verbose=self.verbose)
                    self.log(f"* CACHE_TABLE_NAME {self.cachekv.kv_conn.config.db_info['table']}", verbose=self.verbose)
                    self.log(f"* CACHE_HASH_KEY: {key_hash}.", verbose=self.verbose)
                    self.log(f"* HASH_SEEDS: {cache_key}.", verbose=self.verbose)
                    self.log(f"* CACHED_VALUE: {cached_result}.", verbose=self.verbose)

                    cached_flag = True
                    output = cached_result
                else:
                    self.log("Результата по заданной конфигурации гиперпараметров в кеше нет.", verbose=self.verbose)
                    self.log(f"* CACHE_TABLE_NAME {self.cachekv.kv_conn.config.db_info['table']}", verbose=self.verbose)
                    self.log(f"* CACHE_HASH_KEY: {key_hash}.", verbose=self.verbose)
                    self.log(f"* HASH_SEEDS: {cache_key}.", verbose=self.verbose)

            if not cached_flag:
                self.log("Получем результат с нуля...", verbose=self.verbose)
                output = function(self, *args, **kwargs)

                if self.cachekv is not None:
                    self.log("Кешируем полученный результат.", verbose=self.verbose)
                    self.log(f"* CACHE_TABLE_NAME {self.cachekv.kv_conn.config.db_info['table']}", verbose=self.verbose)
                    self.log(f"* CACHE_HASH_KEY: {key_hash}.", verbose=self.verbose)
                    self.cachekv.save_value(value=output, key_hash=key_hash)

            return output
        return wrapper
