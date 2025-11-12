from abc import ABC, abstractmethod
from typing import List, Dict, Union


class AbstractCacheUtils(ABC):
    @abstractmethod
    def get_cache_key(self, *args, **kwargs) -> List[str]:
        pass
