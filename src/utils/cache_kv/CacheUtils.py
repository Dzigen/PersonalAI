from typing import Union
from copy import deepcopy

from .utils import AbstractCacheUtils
from .CacheKV import CacheKV
from ..tracing import CompositeModuleDetailedResult
from ..errors import ReturnInfo, ReturnStatus
from ...db_drivers.kv_driver import KeyValueDriverConfig


class CacheUtils(AbstractCacheUtils):
    """Реализация утилит для работы с кешем (key-value-хранилищем).

    Класс предоставляет методы для инициализации кеша и декоратор
    для кеширования результатов методов.
    """

    def init_cachekv(self, cache_kvdriver_config: Union[KeyValueDriverConfig, None] = None,
                     cache_table_name: Union[None, str] = None, trace_caching: bool = False) -> Union[None, CacheKV]:
        """Метод предназначен для создания базы данных с целью кеширования требуемых результатов.

        :param cache_kvdriver_config: Конфигурация базы данных для хранения кешируемых результатов. Значение по умолчанию None.
        :type cache_kvdriver_config: Union[KeyValueDriverConfig, None]
        :param cache_table_name: Название таблицы в структуре (базе) данных, куда будут сохраняться (кешироваться) результаты. Значение по умолачанию None.
        :type cache_table_name: Union[None,str], optional
        :param trace_caching: ... . Значение по умолачанию False.
        :type trace_caching: bool, optional
        :return: Если cache_kvdriver_config равен None, то будет возвращен None, иначе будет возвращен интерфейс взаимодействия с созданным кешем.
        :rtype: Union[None, CacheKV]
        """
        cachekv = None
        if cache_kvdriver_config is not None:
            if cache_table_name is None:
                raise ValueError(f"* cache_kvdriver_config: {cache_kvdriver_config}\n* cache_table_name: {cache_table_name}")
            cache_config = deepcopy(cache_kvdriver_config)
            cache_config.db_config.db_info['table'] = cache_table_name
            cachekv = CacheKV(cache_config)
            self.trace_caching = trace_caching

        return cachekv

    def cache_method_output(function):
        """Метод является декоратором для кеширования результатов, возвращаемых от соответствующего (декорируемого) метода.
        Реализация класса, метод которого декорируется, должна содержать get_cache_key-метод для идентификации (генерации ключа) кешируемого результата.
        """

        def wrapper(self, *args, **kwargs):
            cache_hit = False
            cache_key = self.get_cache_key(*args, **kwargs)
            key_hash = None

            if self.cachekv is not None:
                self.log.debug("Поиск результата в кеше...", verbose=self.verbose, log_level=self.log_level)
                cstatus, key_hash, cached_result = self.cachekv.load_value(
                    key=cache_key)
                if cstatus == 0:
                    self.log.debug("Результат по заданной конфигурации гиперпараметров уже был получен.", verbose=self.verbose, log_level=self.log_level)
                    self.log.debug("* cache table_name: %s .", self.cachekv.kv_conn.config.db_info['table'], verbose=self.verbose, log_level=self.log_level)
                    self.log.debug("* cache hash_key: %s .", key_hash, verbose=self.verbose, log_level=self.log_level)
                    self.log.debug("* hash seed: %s .", cache_key, verbose=self.verbose, log_level=self.log_level)
                    self.log.debug("* cached value: %s .", cached_result, verbose=self.verbose, log_level=self.log_level)

                    cache_hit = True
                    output = cached_result
                else:
                    self.log.debug("Результата по заданной конфигурации гиперпараметров в кеше нет.", verbose=self.verbose, log_level=self.log_level)
                    self.log.debug("* cache table_name: %s .", self.cachekv.kv_conn.config.db_info['table'], verbose=self.verbose, log_level=self.log_level)
                    self.log.debug("* cache hash_key: %s.", key_hash, verbose=self.verbose, log_level=self.log_level)
                    self.log.debug("* hash seed: %s .", cache_key, verbose=self.verbose, log_level=self.log_level)

            if not cache_hit:
                self.log.debug("Получаем результат с нуля...", verbose=self.verbose, log_level=self.log_level)
                output = function(self, *args, **kwargs)

                # КОСТЫЛЬ: если во время выполнения функции/метода возникла ошибка,
                # то кеширование полученного результата выполнено не будет.
                # Для детекции данного события функция/метод должна вернуть (в числе прочего) ReturnInfo-структуру.
                is_caching_accepted: bool = True
                if isinstance(output, tuple):
                    for out_item in output:
                        if isinstance(out_item, ReturnInfo):
                            if out_item.status != ReturnStatus.success:
                                is_caching_accepted = False
                            else:
                                break

                if self.cachekv is not None:
                    if is_caching_accepted:
                        self.log.debug("Кешируем полученный результат.", verbose=self.verbose, log_level=self.log_level)
                        self.log.debug("* Trace Caching: %s.", self.trace_caching, verbose=self.verbose, log_level=self.log_level)
                        self.log.debug("* cache table_name: %s", self.cachekv.kv_conn.config.db_info['table'], verbose=self.verbose, log_level=self.log_level)
                        self.log.debug("* cahce hash_key: %s .", key_hash, verbose=self.verbose, log_level=self.log_level)

                        # КОСТЫЛЬ: ...
                        if (not self.trace_caching) and isinstance(output, tuple):
                            save_output = list()
                            for out_item in output:
                                if isinstance(out_item, CompositeModuleDetailedResult):
                                    save_output.append(CompositeModuleDetailedResult())
                                else:
                                    save_output.append(out_item)
                            save_output = tuple(save_output)
                        else:
                            save_output = output

                        self.cachekv.save_value(value=save_output, key_hash=key_hash)
                    else:
                        self.log.warning("Кеширования результата работы метода выполнено не будет, так как во время его выполнения возникла ошибка.", verbose=self.verbose, log_level=self.log_level)

            return *output, cache_hit
        return wrapper
