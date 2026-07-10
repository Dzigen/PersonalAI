from dataclasses import dataclass
from typing import Union, Dict
from ...utils.data_structs import BaseTableStucture


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


AVAILABLE_TABLE_STRUCTURES: Dict[str, BaseTableStucture] = {
    'LLMInferenceStat': LLMInferenceStat
}
