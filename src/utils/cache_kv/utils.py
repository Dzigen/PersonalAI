from abc import ABC, abstractmethod
from typing import List, Dict, Union


class AbstractCacheUtils(ABC):
    """Абстрактный базовый класс для утилит работы с кешем.

    Классы-наследники должны реализовать метод get_cache_key, который формирует детерминированный список строк
    для генерации хеш-ключа в key-value-хранилище.
    """
    @abstractmethod
    def get_cache_key(self, *args, **kwargs) -> List[str]:
        """Метод предназначен для формирования списка строк на основе которого будет генерироваться хеш-ключ.

        :return: Список строковых значений, которые будут использоваться для построения хеш-ключа (cache key).
        :rtype: List[str]
        """
        pass
