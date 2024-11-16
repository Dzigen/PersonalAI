from enum import Enum
from dataclasses import dataclass, field
from typing import List

class ReturnStatus(Enum):
    success = 0
    warning = 1
    error = 2
    #: QA_BAD_QA_PROMPT_MSG, QA_BAD_ENTITIES_EXTRACTION_PROMPT_MSG,
    #: MEM_BAD_THESIS_EXTRACTION_PROMPT_MSG, MEM_BAD_TRIPLET_EXTRACTION_PROMPT_MSG
    bad_format = 3
    #: MEM_ZERO_EXTRACTED_TRIPLETS_MSG
    zero_triplets = 4
    #: QA_ZERO_ENTITIES_MSG
    zero_entities = 5
    #: QA_ZERO_LINKED_NODES_MSG
    zero_linked_nodes = 6
    #: QA_ZERO_RETRIEVED_TRIPLETS_MSG
    zero_retrieved_triplets = 7
    #: QA_EMPTY_ANSWER_MSG
    empty_answer = 8
    #: NOT_SUPPORTED_LANG_MSG
    not_supported_lang = 9
    #: NOT_SUPPORTED_LANG_MSG
    empty_input_text = 10
    #: NOT_SUPPORTED_LANG_MSG
    unknown_lang = 11

#
NOT_SUPPORTED_LANG_MSG = ""
MEM_BAD_TRIPLET_EXTRACTION_PROMPT_MSG = ''
MEM_BAD_THESIS_EXTRACTION_PROMPT_MSG = ''
MEM_ZERO_EXTRACTED_TRIPLETS_MSG = 'Из текста было извлечено нуль триплетов/тезисов.'
QA_BAD_ENTITIES_EXTRACTION_PROMPT_MSG = ''
QA_BAD_QA_PROMPT_MSG = ''
QA_EMPTY_ANSWER_MSG = 'Не удалось получить ответ на вопрос.'
QA_ZERO_ENTITIES_MSG = 'Из вопроса было извлечено ноль сущностей.'
QA_ZERO_LINKED_NODES_MSG = 'Сущностям из вопроса было сопоставлено ноль вершин из используемого графа знаний.'
QA_ZERO_RETRIEVED_TRIPLETS_MSG = 'Было извлечено ноль триплетов из используемого графа знаний.'

@dataclass
class ReturnInfo:
    """Класс предназначен для хранения пояснительной информации к полученному результату в рамках
    некоторой операции.

    :param occurred_warning: Предупреждения, которые возникли в процессе выполнения операции.
    :type occurred_warning: List[ReturnStatus]
    :param status: Статус завершения операции.
    :type status: ReturnStatus
    :param  message: Пояснительное сообщение к статусу возврата.
    :type  message: str
    """
    occurred_warning: List[ReturnStatus] = field(default_factory=lambda: list())
    status: ReturnStatus = ReturnStatus.success
    message: str = ""
