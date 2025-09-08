from abc import ABC, abstractmethod
from typing import List


class AbstractCacheUtils(ABC):
    @abstractmethod
    def get_cache_key(self, *args, **kwargs) -> List[str]:
        pass

    @abstractmethod
    def clear_kv_caches(self, level: str = 'all') -> None:
        # 'current' | 'other' | 'all'
        pass
