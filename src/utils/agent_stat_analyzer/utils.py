from dataclasses import dataclass
from typing import Union
from abc import ABC, abstractmethod

from ...db_drivers.table_driver.utils import BaseTableStucture


@dataclass
class CalculateMetrics:
    count: bool = True
    count_not_null: bool = True
    min: bool = True
    max: bool = True
    median: bool = True
    mean: bool = True
    std: bool = True
    sum: bool = True


@dataclass
class LLMInferenceStat(BaseTableStucture):
    prompt_tokens_amount: int
    generated_tokens_amount: int
    inference_elapsed_time: float  # in seconds
    timestamp: Union[None, str] = None


class AbstractTableStatOperations(ABC):

    @abstractmethod
    def calculate_min(self, column_name: str) -> Union[None, int, float]:
        pass

    @abstractmethod
    def calculate_max(self, column_name: str) -> Union[None, int, float]:
        pass

    @abstractmethod
    def calculate_std(self, column_name: str) -> Union[None, int, float]:
        pass

    @abstractmethod
    def calculate_mean(self, column_name: str) -> Union[None, int, float]:
        pass

    @abstractmethod
    def calculate_median(self, column_name: str) -> Union[None, int, float]:
        pass

    @abstractmethod
    def count_notnull_values(self, column_name: str) -> int:
        pass

    @abstractmethod
    def count_all_values(self, column_name: str) -> int:
        pass

    @abstractmethod
    def calculate_sum(self, column_name: str) -> Union[None, int, float]:
        pass
