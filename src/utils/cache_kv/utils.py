from abc import ABC, abstractmethod
from typing import List, Dict, Union


class AbstractCacheUtils(ABC):
    @abstractmethod
    def get_cache_key(self, *args, **kwargs) -> List[str]:
        pass

    @abstractmethod
    def clear_kv_caches(self, level: str = 'all') -> None:
        # 'current' | 'other' | 'all'
        pass


class AbstractCacheInfo(ABC):
    @abstractmethod
    def get_cache_stat(self) -> Dict[str, Union[None, Dict]]:
        pass

    @abstractmethod
    def get_agent_tgen_stat(self) -> Union[None, Dict[str, Union[None, Dict]]]:
        pass
