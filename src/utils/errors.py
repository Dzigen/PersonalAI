from enum import Enum
from dataclasses import dataclass, field
from typing import List

class ReturnStatus(Enum):
    """_summary_"""
    #
    success = 0
    #
    warning = 1
    #
    error = 2
    #
    bad_format = 3
    #
    zero_triplets = 4
    #
    zero_entities = 5
    #
    zero_linked_nodes = 6
    #
    zero_retrieved_triplets = 7
    #
    empty_answer = 8
    #
    not_supported_lang = 9
    #
    empty_input_text = 10
    #
    unknown_lang = 11

@dataclass
class ReturnInfo:
    """_summary_
    """
    #
    occurred_warning: List[ReturnStatus] = field(default_factory=lambda: list())
    #
    status: ReturnStatus = ReturnStatus.success
    #
    message: str = ""
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
