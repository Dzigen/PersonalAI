import os

from dataclasses import dataclass, fields
from langchain_community.chat_models.gigachat import GigaChat
from typing import Any, Callable, Dict, List, Optional
from abc import ABC, abstractmethod
from typing import Union, Dict
from ..utils import AgentTaskSolverConfig
from ..utils.data_structs import BaseConfigOperations
from dotenv import load_dotenv

load_dotenv(".secrets")
GIGACHAT_KEY = os.getenv("GIGACHAT_KEY")


@dataclass
class BaseStages:
    pass


@dataclass
class BaseTaskSolvers:
    pass


class BaseAgentTaskConfigSelector(ABC):
    @staticmethod
    @abstractmethod
    def get_available_configs() -> None:
        pass

    @staticmethod
    @abstractmethod
    def select(base_config_version: str, cache_table_name: str, inferencestat_table_name: str) -> AgentTaskSolverConfig:
        pass


@dataclass
class BaseAgentTasksConfig(BaseConfigOperations):
    task_to_selector_mapping: Dict[str, BaseAgentTaskConfigSelector]

    @staticmethod
    def from_dict(dict_config: Dict):
        pass

    def to_str(self):
        stringified_config = []
        fields_iterator = fields(self)
        for field_object in fields_iterator:
            if field_object.name == 'task_to_selector_mapping':
                continue

            field_value = getattr(self, field_object.name)

            if isinstance(field_value, str):
                stringified_config.append(f"{field_object.name}={field_value}")
            elif isinstance(field_value, AgentTaskSolverConfig):
                stringified_config.append(f"{field_object.name}={field_value.version}")
            else:
                raise TypeError

        return ";".join(stringified_config)

    def versions_to_configs(self):
        fields_iterator = fields(self)
        for field_object in fields_iterator:
            if field_object.name == 'task_to_selector_mapping':
                continue

            field_value = getattr(self, field_object.name)

            if isinstance(field_value, str):
                task_config_version = field_value
                agent_task_config = self.task_to_selector_mapping[field_object.name].select(base_config_version=task_config_version)
                setattr(self, field_object.name, agent_task_config)


@dataclass
class Message:
    """Внутреннее представление одного сообщения диалога.

    Данный класс используется как удобная оболочка над словарём, описывающим
    отдельное сообщение в рамках сессии диалога. Помимо исходного текста
    сообщения, в нём хранятся дополнительные поля, заполняемые на этапе
    факт-сохраняющей суммаризации.

    :param speaker: Роль говорящего в диалоге (например, ``"user"`` или ``"assistant"``).
    :type speaker: str
    :param dia_id: Идентификатор сообщения в исходном диалоге.
    :type dia_id: str
    :param text: Исходный текст сообщения.
    :type text: str
    :param processed_text: Обработанный текст сообщения (после суммаризации).
        Если суммаризация не выполнялась, может быть равен исходному тексту.
    :type processed_text: str, optional
    :param original_text: Оригинальный текст сообщения, сохранённый перед
        выполнением суммаризации. Если суммаризация не выполнялась, совпадает
        с полем ``text``.
    :type original_text: str, optional
    :param was_summarized: Флаг, показывающий, выполнялась ли для данного
        сообщения факт-сохраняющая суммаризация.
    :type was_summarized: bool
    """

    speaker: str
    dia_id: str
    text: str
    processed_text: Optional[str] = None
    was_summarized: bool = False
    was_reject_while_summarizing: bool = False
    was_reject_while_rephrasing: bool = False
    transformed_text: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Message":
        """Создание экземпляра класса из словаря.

        Ожидается, что переданный словарь содержит как минимум ключи
        ``"speaker"``, ``"dia_id"`` и ``"text"``.

        :param data: Словарь с описанием сообщения.
        :type data: Dict[str, Any]
        :return: Экземпляр ``Message``, инициализированный значениями из словаря.
        :rtype: Message
        """
        return cls(
            speaker=data["speaker"],
            dia_id=data["dia_id"],
            text=data["text"],
            processed_text=data.get("processed_text"),
            was_summarized=data.get("was_summarized", False),
            was_reject_while_summarizing=data.get("was_reject_while_summarizing", False),
            was_reject_while_rephrasing=data.get("was_reject_while_rephrasing", False),
            transformed_text=data.get("transformed_text"),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Преобразует объект сообщения в словарь.

        При отсутствии значения в поле ``processed_text`` в словарь
        будет записан исходный текст сообщения.

        :return: Словарь с описанием сообщения, пригодный для
            последующей сериализации.
        :rtype: Dict[str, Any]
        """
        return {
            "speaker": self.speaker,
            "dia_id": self.dia_id,
            "text": self.text,
            "processed_text": self.processed_text or self.text,
            "was_summarized": self.was_summarized,
            "was_reject_while_summarizing": self.was_reject_while_summarizing,
            "was_reject_while_rephrasing": self.was_reject_while_rephrasing,
            "transformed_text": self.transformed_text,
        }


# Типы колбэков для интеграции с внешней инфраструктурой (LLM, токенизатор).
TokenCounter = Callable[[str], int]

gch_client = GigaChat(
    credentials=GIGACHAT_KEY,
    scope="GIGACHAT_API_PERS",
    verify_ssl_certs=False
)

def count_tokens(text: str):
    return gch_client.get_num_tokens(text)


Summarizer = Callable[[str, Optional[str], Optional[str]], str]


def preprocess_dialog_step0_fact_preserving(
    dialog: Dict[str, List[Dict[str, Any]]],
    *,
    max_chunk_tokens: int,
    count_tokens: TokenCounter,
    summarize_fact_preserving: Summarizer,
    neighbor_max_tokens: int,
) -> Dict[str, List[Dict[str, Any]]]:
    """Выполняет факт-сохраняющую суммаризацию длинных сообщений в диалоге.

    Функция проходит по всем сессиям и сообщениям диалога. Для каждого
    сообщения подсчитывается количество токенов. Если длина сообщения
    не превышает ``max_chunk_tokens``, то оно переносится без изменений,
    при этом поля ``processed_text`` и ``original_text`` заполняются
    исходным текстом, а флаг ``was_summarized`` устанавливается в ``False``.
    Если длина сообщения превышает лимит, выполняется факт-сохраняющая
    суммаризация с использованием переданного колбэка
    ``summarize_fact_preserving`` и краткого контекста из соседних сообщений.

    Формат входного диалога:
        ``dialog = { "session_1": [ { "speaker": ..., "dia_id": ..., "text": ... }, ... ], ... }``

    :param dialog: Диалог, представленный в виде словаря, где ключи —
        идентификаторы сессий, а значения — списки сообщений.
    :type dialog: Dict[str, List[Dict[str, Any]]]
    :param max_chunk_tokens: Лимит токенов для одного сообщения. Если длина
        сообщения превышает данный лимит, выполняется факт-сохраняющая
        суммаризация.
    :type max_chunk_tokens: int
    :param count_tokens: Функция для подсчёта числа токенов в тексте для
        выбранной LLM-модели.
    :type count_tokens: TokenCounter
    :param summarize_fact_preserving: Функция для выполнения
        факт-сохраняющей суммаризации одного сообщения. На вход получает
        исходный текст сообщения и краткий контекст до/после него.
    :type summarize_fact_preserving: Summarizer
    :param neighbor_max_tokens: Максимальное число токенов, которое можно
        использовать для формирования контекста из соседних сообщений
        (отдельно для предыдущего и последующего сообщения).
    :type neighbor_max_tokens: int
    :return: Новый словарь с сессиями и сообщениями, в котором для каждого
        сообщения заполнены поля ``processed_text``, ``original_text`` и
        ``was_summarized``.
    :rtype: Dict[str, List[Dict[str, Any]]]
    """
    processed_dialog: Dict[str, List[Dict[str, Any]]] = {}

    cnt_sessions = 1
    while True:
        if f"session_{cnt_sessions}" in dialog:
            cnt_sessions += 1
        else:
            break
    cnt_sessions -= 1

    for i in range(cnt_sessions):
        session_id = f"session_{i+1}"
        raw_messages = dialog[session_id]
        # Преобразуем входные словари в объекты Message
        messages: List[Message] = [Message.from_dict(m) for m in raw_messages]

        for idx, msg in enumerate(messages):
            token_count = count_tokens(msg.text)

            if token_count <= max_chunk_tokens:
                # Короткие сообщения оставляем без изменений
                msg.processed_text = msg.text
                msg.was_summarized = False
                continue

            # Сообщение длиннее max_chunk_tokens: выполняем факт-сохраняющую суммаризацию

            prev_context = _truncate_neighbor(
                messages[idx - 1].text if idx > 0 else None,
                count_tokens,
                neighbor_max_tokens,
            )
            next_context = _truncate_neighbor(
                messages[idx + 1].text if idx + 1 < len(messages) else None,
                count_tokens,
                neighbor_max_tokens,
            )

            summarized = summarize_fact_preserving(
                msg.text,
                prev_context if prev_context else "",
                next_context if next_context else "",
            )

            msg.processed_text = summarized
            msg.was_summarized = True

        processed_dialog[session_id] = [m.to_dict() for m in messages]

    return processed_dialog


def _truncate_neighbor(
    text: Optional[str],
    count_tokens: TokenCounter,
    neighbor_max_tokens: int,
) -> Optional[str]:
    """Обрезает соседнее сообщение по ограничению на число токенов.

    Вспомогательная функция, используемая при подготовке краткого контекста
    из соседних сообщений. Если входной текст отсутствует, возвращается None.

    :param text: Текст соседнего сообщения.
    :type text: Optional[str]
    :param count_tokens: Функция для подсчёта числа токенов в тексте.
    :type count_tokens: TokenCounter
    :param neighbor_max_tokens: Максимальное число токенов в усечённом тексте.
    :type neighbor_max_tokens: int
    :return: Усечённый текст соседнего сообщения или None.
    :rtype: Optional[str]
    """
    if text is None:
        return None

    # Простейшая реализация: обрезаем по словам, пока не будет превышен лимит.
    words = text.split()
    acc_words: List[str] = []
    acc_tokens = 0

    for w in words:
        t = count_tokens(w)
        if acc_tokens + t > neighbor_max_tokens:
            break
        acc_words.append(w)
        acc_tokens += t

    if acc_words:
        return " ".join(acc_words)

    # Fallback на случай некорректной оценки токенов функцией count_tokens.
    return text[:512]
