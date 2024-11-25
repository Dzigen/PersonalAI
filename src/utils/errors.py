from enum import Enum
from dataclasses import dataclass, field
from typing import List

class ReturnStatus(Enum):
    success = 0
    empty_input_text: 1
    bad_formater: 2
    bad_parser: 3
    bad_postprocessor: 4
    not_supported_lang = 5
    unknown_lang = 6
    empty_answer = 7
    zero_entities = 8
    zero_linked_nodes = 9
    zero_retrieved_triplets = 10

    zero_triplets = 4

STATUS_MESSAGE = {
    ReturnStatus.success: "Операция выполнена успешно.",
    ReturnStatus.empty_input_text: "",
    # agent solver
    ReturnStatus.bad_formater: "Не удалось привести данные в context-формат для их дальнейшей вставки в user-prompt.",
    ReturnStatus.bad_parser: "Не удалось разобрать ответ LLM-агента.",
    ReturnStatus.bad_postprocessor: "Не удалось привести разобранный ответ LLM-агента к заданному формату.",
    # detect language
    ReturnStatus.not_supported_lang: "",
    ReturnStatus.unknown_lang: "",
    # qa-pipeline (answer generation)
    ReturnStatus.empty_answer: 'Не удалось получить ответ на вопрос.',
    # qa-pipeline (query parser)
    ReturnStatus.zero_entities: 'Из вопроса было извлечено нуль сущностей.',
    # qa-pipeline (knowledge comparator)
    ReturnStatus.zero_linked_nodes: 'Сущностям из вопроса было сопоставлено ноль вершин из используемого графа знаний.',
    # qa-pipeline (knowledge retriever)
    ReturnStatus.zero_retrieved_triplets: 'Было извлечено ноль триплетов из используемого графа знаний.',
    # memorize-pipeline (extractor)
    # TODO
    # memorize-pipeline (updator)
    # TODO
}

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
