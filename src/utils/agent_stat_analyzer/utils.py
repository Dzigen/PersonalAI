from dataclasses import dataclass
from typing import Union
from abc import ABC, abstractmethod


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
