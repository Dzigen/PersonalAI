from typing import List, Dict
from abc import ABC, abstractmethod
from dataclasses import dataclass, field


class AbstractRetriverModule(ABC):

    @abstractmethod
    def run(self):
        # TODO
        pass
