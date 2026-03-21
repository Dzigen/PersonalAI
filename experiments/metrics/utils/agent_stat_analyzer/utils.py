from dataclasses import dataclass
from typing import Union
from abc import ABC, abstractmethod

from ..db_drivers.table_driver.utils import BaseTableStucture


@dataclass
class CalculateMetrics:
    """Флаги, задающие, какие агрегирующие метрики необходимо вычислять по статистике LLM-инференса.

    Каждый атрибут отвечает за включение или отключение одноимённой метрики.
    """
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
    """Структура данных для хранения статистики одной inference-операции LLM.

    :param prompt_tokens_amount: Количество токенов во входном промпте.
    :type prompt_tokens_amount: int
    :param generated_tokens_amount: Количество токенов, сгенерированных моделью.
    :type generated_tokens_amount: int
    :param inference_elapsed_time: Время инференса в секундах.
    :type inference_elapsed_time: float
    :param timestamp: Временная метка записи в БД.
    :type timestamp: Union[None, str]
    """
    prompt_tokens_amount: int
    generated_tokens_amount: int
    inference_elapsed_time: float  # in seconds
    timestamp: Union[None, str] = None


class AbstractTableStatOperations(ABC):
    """Абстрактный интерфейс операций над табличным хранилищем статистики.

    Конкретные реализации должны предоставлять вычисление агрегирующих метрик (min, max, mean, median, std, суммарное количество и число ненулевых значений)
    для числовых колонок таблицы статистики.
    """

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
        """Возвращает общее количество записей в таблице."""
        pass

    @abstractmethod
    def calculate_sum(self, column_name: str) -> Union[None, int, float]:
        pass
