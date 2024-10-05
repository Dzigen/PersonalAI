from typing import List, Tuple, Dict
from dataclasses import dataclass

@dataclass
class RetrieverCacheConfig:
    # TODO
    pass

class RetrieverCache:
    def __init__(self, config: RetrieverCacheConfig = RetrieverCacheConfig()) -> None:
        # TODO
        self.config = config

    def key_exist() -> bool:
        # TODO
        pass

    def get_value_by_key(key: str) -> Dict:
        # TODO
        pass