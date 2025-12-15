from copy import deepcopy
from dataclasses import dataclass, field
from .config import CHNKBLD_MAIN_LOG_PATH
from typing import Tuple, Union, List, Dict, Callable, Optional, Any
from ..utils import TokenCounter
from ...utils import ReturnInfo, Logger
from ...utils.data_structs import create_id, QueryPreprocessingInfo, BaseComponentConfig, LanguageConfig


@dataclass
class ChunkBuildConfig(BaseComponentConfig, LanguageConfig):
    """
    """
    chunk_max_tokens: int = 4000
    chunk_overlap_tokens: int = 600

    log: Logger = field(default_factory=lambda: Logger(CHNKBLD_MAIN_LOG_PATH))

    @staticmethod
    def from_dict(dict_config: Dict):
        dictconfig_copy = deepcopy(dict_config)
        formated_config = ChunkBuildConfig(**dictconfig_copy)
        formated_config.formate_fields()
        return formated_config

    def formate_fields(self):
        pass


class ChunkBuild():
    """
    """
    def __init__(self, config: Union[Dict, ChunkBuildConfig] = ChunkBuildConfig()) -> None:
        if isinstance(config, dict):
            config: ChunkBuildConfig = ChunkBuildConfig.from_dict(config)
        else:
            config.formate_fields()
        self.config = config

        self.log = self.config.log
        self.verbose = self.config.verbose

    def perform(
        self,
        session_messages: List[Dict[str, Any]],
        message_groups: List[List[int]],
        count_tokens: TokenCounter,
    ) -> List[Dict[str, Any]]:
        """Разбивает группы сообщений одной сессии на чанки с overlap.

        Правила:
            1. Основной приоритет — максимально возможное число сообщений в чанке
            при соблюдении лимита chunk_max_tokens.
            2. Если весь хвост группы (от текущего start_pos до конца) помещается
            в лимит, чанк строится по всему хвосту целиком, даже если последнее
            сообщение — пользователь.
            3. Если разрыв неизбежен (хвост не помещается), конец чанка сдвигается
            назад до последнего сообщения ассистента в диапазоне
            [start_pos .. last_pos], если ассистент там есть.
            4. Каждый следующий чанк должен содержать хотя бы одно новое сообщение,
            которого не было в предыдущих чанках данной группы (по индексам
            внутри группы).
            5. Между чанками формируется overlap по токенам (по возможности):
            новый чанк стартует так, чтобы хвост предыдущего чанка
            перекрывался минимум на chunk_overlap_tokens, но правило (4) имеет
            более высокий приоритет: при конфликте overlap может быть уменьшен
            вплоть до нуля.

        :param session_messages: Список сообщений одной сессии диалога.
        :type session_messages: List[Dict[str, Any]]
        :param message_groups: Группы сообщений (user + отфильтрованные assistant),
            каждая группа — список индексов в session_messages.
        :type message_groups: List[List[int]]
        :param count_tokens: Функция для подсчёта числа токенов в тексте.
        :type count_tokens: TokenCounter
        :param chunk_max_tokens: Максимальное количество токенов в одном чанке.
        :type chunk_max_tokens: int
        :param chunk_overlap_tokens: Желаемое количество токенов перекрытия между чанками.
        :type chunk_overlap_tokens: int
        :return: Список чанков, каждый чанк описывается словарём с полями
            ``group_index`` и ``message_indices`` (индексы в session_messages).
        :rtype: List[Dict[str, Any]]
        """
        chunks: List[Dict[str, Any]] = []

        # Предрасчёт числа токенов для всех сообщений сессии
        token_counts: List[int] = []
        for msg in session_messages:
            text = msg.get("processed_text") or msg.get("text") or ""
            token_counts.append(count_tokens(text))

        for group_idx, group_indices in enumerate(message_groups):
            if not group_indices:
                continue

            group_indices_sorted = sorted(group_indices)
            n = len(group_indices_sorted)

            # Максимальная позиция (в терминах позиции в group_indices_sorted),
            # которая уже была покрыта предыдущими чанками этой группы.
            prev_last_pos: int = -1

            pos = 0
            while pos < n:
                start_pos = pos

                # --- Шаг 1. Набираем максимально длинный префикс по токенам ---
                token_sum = 0
                last_pos: Optional[int] = None
                i = start_pos

                while i < n:
                    msg_idx = group_indices_sorted[i]
                    t = token_counts[msg_idx]

                    # Разрешаем первое сообщение в чанке даже в том случае,
                    # если оно само по себе длиннее chunk_max_tokens.
                    # В нормальном сценарии такого не будет, так как длинные
                    # сообщения обрезаются/суммаризуются на шаге 0.
                    if token_sum > 0 and token_sum + t > self.config.chunk_max_tokens:
                        break

                    token_sum += t
                    last_pos = i
                    i += 1

                if last_pos is None:
                    # На всякий случай, если ничего не добавили:
                    last_pos = start_pos
                    msg_idx = group_indices_sorted[start_pos]
                    token_sum = token_counts[msg_idx]

                # last_pos — позиция последнего сообщения, которое помещается в лимит
                # full_tail_fits == True, если целый хвост [start_pos .. n-1] влез
                full_tail_fits = (last_pos == n - 1 and token_sum <= self.config.chunk_max_tokens)

                # --- Шаг 2. Определяем end_pos с учётом ассистента ---
                if full_tail_fits:
                    # Весь хвост помещается в один чанк — НЕ режем по ассистенту,
                    # просто берём всё до конца группы.
                    end_pos = last_pos
                else:
                    # Разрыв неизбежен: корректируем конец чанка так, чтобы
                    # последнее сообщение было ассистентом, если он есть.
                    end_pos = last_pos
                    last_assistant_pos: Optional[int] = None
                    for p in range(last_pos, start_pos - 1, -1):
                        msg_idx = group_indices_sorted[p]
                        if session_messages[msg_idx].get("speaker") == "assistant":
                            last_assistant_pos = p
                            break

                    if last_assistant_pos is not None:
                        end_pos = last_assistant_pos
                    else:
                        end_pos = last_pos

                if end_pos < start_pos:
                    end_pos = start_pos

                # --- Шаг 3. Проверка, что чанк добавляет новые сообщения ---
                # prev_last_pos — максимальная позиция внутри группы, уже
                # покрытая предыдущими чанками. Требуем, чтобы текущий чанк
                # содержал хотя бы одну позицию > prev_last_pos.
                if end_pos <= prev_last_pos:
                    # Этот чанк целиком лежит в уже покрытой зоне.
                    # Пропускаем его и двигаем старт дальше за prev_last_pos.
                    new_start = prev_last_pos + 1
                    if new_start >= n:
                        break
                    pos = new_start
                    continue

                # --- Шаг 4. Собираем финальный список индексов сообщений чанка ---
                chunk_message_indices = [
                    group_indices_sorted[i] for i in range(start_pos, end_pos + 1)
                ]

                if not chunk_message_indices:
                    # На всякий случай, чтобы не зациклиться
                    new_start = max(start_pos + 1, prev_last_pos + 1)
                    if new_start >= n:
                        break
                    pos = new_start
                    continue

                chunks.append(
                    {
                        "group_index": group_idx,
                        "message_indices": chunk_message_indices,
                    }
                )
                prev_last_pos = end_pos

                # Если дошли до конца группы — выходим из цикла по группе
                if end_pos == n - 1:
                    break

                # --- Шаг 5. Формируем overlap для следующего чанка ---
                # Идём назад от end_pos, пока не наберём chunk_overlap_tokens.
                overlap_sum = 0
                p = end_pos
                while p >= start_pos and overlap_sum < self.config.chunk_overlap_tokens:
                    msg_idx = group_indices_sorted[p]
                    overlap_sum += token_counts[msg_idx]
                    p -= 1

                overlap_start_pos = max(start_pos, p + 1)

                # Здесь overlap_start_pos in [start_pos .. end_pos].
                # Новый старт pos задаём через overlap, но при этом помним,
                # что следующий чанк всё равно будет проверен на добавление
                # новых сообщений (через prev_last_pos), так что зацикливания
                # не будет: если из overlap-области нельзя построить чанк с
                # новыми сообщениями, старт будет сдвинут за prev_last_pos.

                if overlap_start_pos >= n:
                    break

                pos = overlap_start_pos

        return chunks
