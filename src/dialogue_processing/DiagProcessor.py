
from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Union

from .utils import (
    TokenCounter,
    preprocess_dialog_step0_fact_preserving,
)
from ..agents.utils import AbstractAgentConnector
from .fact_preserving import FactPreserverConfig
from .fact_preserving.FactPreserver import FactPreserv
from .same_context_clf import SameContextClfConfig
from .same_context_clf.ContextClassifier import SameContextClf
from .assistant_useful_cls import AssistUsefulClf, AssistUsefulClfConfig
from .chunk_builder import ChunkBuild, ChunkBuildConfig
from .chunk_rephraser import RephraseChunk, RephraseChunkConfig
from ..db_drivers.kv_driver import KeyValueDriverConfig
from ..utils import Logger
from ..utils.data_structs import BaseComponentConfig, LanguageConfig
from .configs import DP_MAIN_LOG_PATH, DEFAULT_DIAG_PROC_KVCACHE_CONFIG
from ..utils.cache_kv import CacheUtils
from ..utils.cache_kv.CacheOperations import CacheOperations


@dataclass
class DiagProcessorConfig(BaseComponentConfig, LanguageConfig):
    """Конфигурация конвейера обработки диалогов.

    """
    fact_preserver_config: Union[Dict, FactPreserverConfig] = field(
        default_factory=lambda: FactPreserverConfig())
    context_clf_config: Union[Dict, SameContextClfConfig] = field(
        default_factory=lambda: SameContextClfConfig())
    assist_use_clf_config: Union[Dict, AssistUsefulClfConfig] = field(
        default_factory=lambda: AssistUsefulClfConfig())
    chunk_build_config: Union[Dict, ChunkBuildConfig] = field(
        default_factory=lambda: ChunkBuildConfig())
    rephrase_chunk_config: Union[Dict, RephraseChunkConfig] = field(
        default_factory=lambda: RephraseChunkConfig())

    log: Logger = field(default_factory=lambda: Logger(DP_MAIN_LOG_PATH))

    def to_str(self):
        # TODO
        raise NotImplementedError

    @staticmethod
    def from_dict(dict_config: Dict):
        dictconfig_copy = deepcopy(dict_config)
        formated_config = DiagProcessorConfig(**dictconfig_copy)
        formated_config.formate_fields()
        return formated_config

    def formate_fields(self):
        if isinstance(self.fact_preserver_config, dict):
            self.fact_preserver_config = FactPreserverConfig.from_dict(self.fact_preserver_config)
        else:
            self.fact_preserver_config.formate_fields()

        if isinstance(self.context_clf_config, dict):
            self.context_clf_config = SameContextClfConfig.from_dict(self.context_clf_config)
        else:
            self.context_clf_config.formate_fields()

        if isinstance(self.assist_use_clf_config, dict):
            self.assist_use_clf_config = AssistUsefulClfConfig.from_dict(self.assist_use_clf_config)
        else:
            self.assist_use_clf_config.formate_fields()

        if isinstance(self.chunk_build_config, dict):
            self.chunk_build_config = ChunkBuildConfig.from_dict(self.chunk_build_config)
        else:
            self.chunk_build_config.formate_fields()

        if isinstance(self.rephrase_chunk_config, dict):
            self.rephrase_chunk_config = RephraseChunkConfig.from_dict(self.rephrase_chunk_config)
        else:
            self.rephrase_chunk_config.formate_fields()


class DiagProc(CacheOperations):
    """Верхнеуровневый класс для предварительной обработки диалоговых данных.

    Основная задача данного класса — подготовка диалогов к последующему запуску memorize-/qa-пайплайнов.

    Формат входных данных:
        dialogues: List[Dict], где каждый элемент имеет структуру:
        {
            "qa": <список вопросов, в текущем шаге не используется>,
            "conversation": {
                "session_1": [ { "speaker": ..., "dia_id": ..., "text": ... }, ... ],
                "session_2": [...],
                ...
            }
        }

    :param dialogues: Список диалогов, подлежащих обработке.
    :type dialogues: List[Dict[str, Any]]
    :param agent: Коннектор к конкретному LLM-агенту для выполнения inference-операций.
    :type agent: AbstractAgentConnector
    :param count_tokens: Функция для подсчёта числа токенов в строке текста для выбранной LLM-модели.
    :type count_tokens: TokenCounter
    :param config: Конфигурация конвейера обработки диалогов. По умолчанию используется DiagProcessorConfig() c параметрами по умолчанию.
    :type config: Optional[DiagProcessorConfig], optional
    :param cache_kvdriver_config: Конфигурация структуры данных для кеширования промежуточных результатов в рамках компонент данного класса. Значение по умолчанию None.
    :type cache_kvdriver_config: Union[KeyValueDriverConfig, None], optional
    """

    def __init__(
        self,
        dialogues: List[Dict[str, Any]],
        agent: AbstractAgentConnector,
        count_tokens: TokenCounter,
        config: Union[Dict, DiagProcessorConfig] = DiagProcessorConfig(),
        cache_kvdriver_config: Union[KeyValueDriverConfig, None] = DEFAULT_DIAG_PROC_KVCACHE_CONFIG
    ) -> None:
        if isinstance(config, dict):
            config: DiagProcessorConfig = DiagProcessorConfig.from_dict(config)
        else:
            config.formate_fields()

        self.config = config

        self.dialogues: List[Dict[str, Any]] = dialogues
        self.count_tokens: TokenCounter = count_tokens

        self.fact_preserver: FactPreserv = FactPreserv(
            agent, config.fact_preserver_config, cache_kvdriver_config
        )
        self.same_context_clf: SameContextClf = SameContextClf(
            agent, config.context_clf_config, cache_kvdriver_config
        )
        self.assistant_useful_clf: AssistUsefulClf = AssistUsefulClf(
            agent, config.assist_use_clf_config, cache_kvdriver_config
        )
        self.chunk_builder: ChunkBuild = ChunkBuild(
            config.chunk_build_config
        )
        self.rephrase_chunk: RephraseChunk = RephraseChunk(
            agent, config.rephrase_chunk_config, cache_kvdriver_config
        )

        self.log = config.log
        self.verbose = config.verbose


    def run_step0_fact_preserving(self) -> List[Dict[str, Any]]:
        """Запускает шаг 0: факт-сохраняющую суммаризацию длинных сообщений.

        Для каждого диалога из self.dialogues проходит по всем сессиям и сообщениям, подсчитывает количество токенов в сообщении и, если длина
        сообщения превышает max_chunk_tokens, выполняет факт-сохраняющую суммаризацию с использованием компоненты fact_preserver и краткого
        контекста (предыдущее и следующее сообщение в сессии, обрезанные по neighbor_max_tokens).

        Результат записывается обратно в поле "conversation" каждого диалога,
        причём для каждого сообщения добавляются поля:
         - processed_text
         - original_text
         - was_summarized

        :return: Список диалогов с обновлённым содержимым поля "conversation".
        :rtype: List[Dict[str, Any]]
        """
        self.log("START MESSAGE SUMMARY...", verbose=self.verbose)
        for dialog in self.dialogues:
            conversation = dialog.get("conversation")

            if not isinstance(conversation, dict):
                continue

            processed_conversation = preprocess_dialog_step0_fact_preserving(
                dialog=conversation,
                max_chunk_tokens=self.config.fact_preserver_config.max_chunk_tokens,
                count_tokens=self.count_tokens,
                summarize_fact_preserving=self._summarize_with_fact_preserver,
                neighbor_max_tokens=self.config.fact_preserver_config.neighbor_max_tokens,
            )

            dialog["conversation"] = processed_conversation

        return self.dialogues


    def run_step1_group_user_messages(self) -> List[Dict[str, Any]]:
        """Запускает шаг 1: формирование смысловых групп по user-сообщениям.

        Для каждого диалога и каждой его сессии формирует группы пользовательских сообщений по следующему правилу:
            1. Первое пользовательское сообщение в сессии всегда начинает первую группу.
            2. Для каждого следующего пользовательского сообщения U_i:
               - A: предыдущее пользовательское сообщение в ТЕКУЩЕЙ группе;
               - B: текущее пользовательское сообщение U_i.
               - Вызывается классификатор is_same_context(A.text, B.text).
               - Если результат True, U_i добавляется в текущую группу.
               - Если результат False, текущая группа закрывается, и U_i становится первым элементом новой группы.

        Результаты группировки записываются в поле "user_message_groups" каждого диалога.

        :return: Список диалогов с добавленным полем "user_message_groups".
        :rtype: List[Dict[str, Any]]
        """
        self.log("START GROUPING MESSAGES...", verbose=self.verbose)
        for dialog in self.dialogues:
            conversation = dialog.get("conversation")
            if not isinstance(conversation, dict):
                continue

            session_groups: Dict[str, List[List[int]]] = {}

            for session_id, session_messages in conversation.items():
                if not isinstance(session_messages, list):
                    continue

                groups_for_session = self._group_user_messages_in_session(session_messages=session_messages)
                session_groups[session_id] = groups_for_session

            dialog["user_message_groups"] = session_groups

        return self.dialogues


    def run_step2_filter_assistant_messages(self) -> List[Dict[str, Any]]:
        """Запускает шаг 2: добавление ассистентских сообщений через LLM-фильтр.

        На вход подаются уже сформированные на шаге 1 группы пользовательских сообщений, записанные в поле dialog["user_message_groups"] в формате:
            dialog["user_message_groups"] = {
                "session_1": [
                    [i_11, i_12, ...],  # группа 1: индексы user-сообщений
                    [i_21, i_22, ...],  # группа 2
                    ...
                ],
                "session_2": [...],
                ...
            }

        Для каждой сессии и каждой группы пользовательских сообщений метод рассматривает ассистентские сообщения, попадающие внутрь диапазона
        группы, и с помощью LLM решает, включать их в группу или нет.

        Внутри диапазона каждая группа превращается в последовательность индексов сообщений (user + отфильтрованные assistant) в исходном порядке.
        Результаты записываются в поле "message_groups" каждого диалога.

        :return: Список диалогов с добавленным полем "message_groups".
        :rtype: List[Dict[str, Any]]
        """
        self.log("START FILTERING ASSISTANT MESSAGES...", verbose=self.verbose)
        for dialog in self.dialogues:
            conversation = dialog.get("conversation")
            user_groups_map = dialog.get("user_message_groups")

            if not isinstance(conversation, dict) or not isinstance(user_groups_map, dict):
                # Если нет корректных данных о сессиях или группах пользователей, пропускаем диалог.
                continue

            session_message_groups: Dict[str, List[List[int]]] = {}

            for session_id, session_messages in conversation.items():
                if not isinstance(session_messages, list):
                    continue

                user_groups = user_groups_map.get(session_id)
                if not user_groups:
                    # В этой сессии нет групп пользовательских сообщений.
                    session_message_groups[session_id] = []
                    continue

                groups_with_assistant = self._build_message_groups_with_assistant(session_messages=session_messages, user_groups=user_groups)
                session_message_groups[session_id] = groups_with_assistant

            dialog["message_groups"] = session_message_groups

        return self.dialogues


    def run_step3_build_chunks(self) -> List[Dict[str, Any]]:
        """Запускает шаг 3: разбиение групп сообщений на чанки с overlap.

        Для каждой группы в каждой сессии выполняется разбиение на чанки
        по следующим правилам:
         - сообщения рассматриваются в порядке их индексов в группе;
         - длина чанка в токенах не должна превышать chunk_max_tokens;
         - между соседними чанками одной группы создаётся перекрытие по токенам размером не менее chunk_overlap_tokens;
         - последнее сообщение в чанке по возможности должно быть сообщением ассистента. Если в рассматриваемом диапазоне нет сообщений ассистента, правило нарушается (fallback).

        Результат записывается в поле dialog["chunks"] каждого диалога в формате:
            dialog["chunks"] = {
                "session_1": [
                    {"group_index": 0, "message_indices": [idx_1, idx_2, ...]},
                    {"group_index": 0, "message_indices": [...]},
                    {"group_index": 1, "message_indices": [...]},
                    ...
                ],
                "session_2": [...],
                ...
            }

        :return: Список диалогов с добавленным полем "chunks".
        :rtype: List[Dict[str, Any]]
        """
        self.log("START BUILDING CHUNKS...", verbose=self.verbose)
        for dialog in self.dialogues:
            conversation = dialog.get("conversation")
            message_groups_map = dialog.get("message_groups")

            if not isinstance(conversation, dict) or not isinstance(message_groups_map, dict):
                continue

            session_chunks: Dict[str, List[Dict[str, Any]]] = {}

            for session_id, session_messages in conversation.items():
                self.log(f"Building chunks for {session_id}", verbose=self.verbose)
                if not isinstance(session_messages, list):
                    continue

                groups_for_session = message_groups_map.get(session_id)
                if not groups_for_session:
                    session_chunks[session_id] = []
                    continue

                chunks_for_session = self.chunk_builder.perform(
                    session_messages=session_messages,
                    message_groups=groups_for_session,
                    count_tokens=self.count_tokens
                )
                session_chunks[session_id] = chunks_for_session

            dialog["chunks"] = session_chunks

        return self.dialogues


    def run_step4_rephrase_messages(self) -> List[Dict[str, Any]]:
        """Запускает шаг 5: переформулирование сообщений в чанках под memorize-пайплайн.

        Для каждого чанка берутся сообщения по индексам message_indices в соответствующей сессии, передаются в компонент переформулирования (rephrase_chunk), и результат записывается в поле "transformed_text" каждого сообщения.

        :return: Список диалогов с обновлённым содержимым "conversation".
        :rtype: List[Dict[str, Any]]
        """
        self.log("START REPHRASING...", verbose=self.verbose)
        for dialog in self.dialogues:
            conversation = dialog.get("conversation")
            chunks_by_session = dialog.get("chunks")

            if not isinstance(conversation, dict) or not isinstance(chunks_by_session, dict):
                continue

            for session_id, session_chunks in chunks_by_session.items():
                session_messages = conversation.get(session_id)
                if not isinstance(session_messages, list):
                    continue

                if not isinstance(session_chunks, list):
                    continue

                for chunk_desc in session_chunks:
                    msg_indices = chunk_desc.get("message_indices")
                    if not isinstance(msg_indices, list) or not msg_indices:
                        continue

                    # Собираем сообщения чанка в исходном порядке.
                    chunk_messages: List[Dict[str, Any]] = []
                    for idx in msg_indices:
                        # Защита от выхода за пределы списка сообщений.
                        if not isinstance(idx, int) or idx < 0 or idx >= len(session_messages):
                            continue
                        chunk_messages.append(session_messages[idx])

                    if not chunk_messages:
                        continue

                    parsed_responce, raw_responce, is_reject_answer = self.rephrase_chunk.perform(chunk_messages)

                    if not parsed_responce:
                        continue

                    chunk_desc['transformed_msgs'] = raw_responce
                    chunk_desc['was_reject_while_rephrasing'] = is_reject_answer

                    if is_reject_answer:
                        for local_i, msg in enumerate(chunk_messages):
                            global_idx = msg_indices[local_i]
                            if (not isinstance(global_idx, int) or global_idx < 0 or global_idx >= len(session_messages)):
                                continue

                            target_msg = session_messages[global_idx]

                            target_msg["transformed_text"] = msg.get("processed_text") or msg.get("text") or ""
                            target_msg["was_reject_while_rephrasing"] = True
                        continue

                    if len(parsed_responce) != len(chunk_messages):
                        self.log(f"Number of rephrased msgs ({len(parsed_responce)}) doesn't equal to number of passed msgs ({len(chunk_messages)})", verbose=self.verbose)

                    # Записываем переформулированный текст в сообщения.
                    for local_i, msg in enumerate(chunk_messages):
                        if local_i < len(parsed_responce):
                            new_text = parsed_responce[local_i]
                        else:
                            new_text = parsed_responce[-1]

                        # Соответствующий индекс в session_messages.
                        # Мы восстанавливаем его через msg_indices, а не через поиск по dia_id, так надёжнее в рамках текущей структуры.
                        global_idx = msg_indices[local_i]
                        if (not isinstance(global_idx, int) or global_idx < 0 or global_idx >= len(session_messages)):
                            continue

                        target_msg = session_messages[global_idx]

                        target_msg["transformed_text"] = new_text

        return self.dialogues


    def _summarize_with_fact_preserver(
        self,
        text: str,
        prev_context: Optional[str],
        next_context: Optional[str],
    ) -> str:
        """Обёртка над FactPreserv.perform для согласования сигнатур.

        :param text: Текст сообщения, подлежащего факт-сохраняющей суммаризации.
        :type text: str
        :param prev_context: Краткий контекст из предыдущего сообщения (или None, если предыдущего сообщения нет).
        :type prev_context: Optional[str]
        :param next_context: Краткий контекст из следующего сообщения (или None, если следующего сообщения нет).
        :type next_context: Optional[str]
        :return: Суммаризованный текст, в котором сохранены факты и связи.
        :rtype: str
        """
        return self.fact_preserver.perform(
            text=text,
            prev_context=prev_context,
            next_context=next_context,
        )


    def _group_user_messages_in_session(
        self,
        session_messages: List[Dict[str, Any]],
    ) -> List[List[int]]:
        """Формирует смысловые группы по пользовательским сообщениям в одной сессии.

        :param session_messages: Список сообщений одной сессии диалога. Каждый элемент - словарь с полями как минимум "speaker" и "text".
        :type session_messages: List[Dict[str, Any]]
        :return: Список групп пользовательских сообщений в виде списков индексов.
        :rtype: List[List[int]]
        """
        # Индексы всех user-сообщений в сессии
        user_indices: List[int] = [
            idx for idx, msg in enumerate(session_messages) if msg.get("speaker") == "user"
        ]

        if not user_indices:
            return []

        groups: List[List[int]] = []

        # Первая группа начинается с первого пользовательского сообщения
        current_group: List[int] = [user_indices[0]]
        prev_user_text: str = session_messages[user_indices[0]].get("processed_text", "")

        # Проходим по остальным пользовательским сообщениям
        for idx in user_indices[1:]:
            curr_msg = session_messages[idx]
            curr_text: str = curr_msg.get("processed_text", "")

            same_context = self.same_context_clf.perform(prev_user_text, curr_text)

            if same_context:
                current_group.append(idx)
                prev_user_text = curr_text
            else:
                # Закрываем текущую группу и начинаем новую
                groups.append(current_group)
                current_group = [idx]
                prev_user_text = curr_text

        # Добавляем последнюю группу
        if current_group:
            groups.append(current_group)

        return groups


    def _build_message_groups_with_assistant(
        self,
        session_messages: List[Dict[str, Any]],
        user_groups: List[List[int]]
    ) -> List[List[int]]:
        """Формирует группы сообщений (user + отфильтрованные assistant) в одной сессии.

        На вход подаются:
            - session_messages: исходный список сообщений сессии
            (user и assistant в хронологическом порядке);
            - user_groups: результат шага 1, список групп пользовательских сообщений,
            где каждая группа — это список индексов user-сообщений в session_messages;
            - is_assistant_useful: функция-фильтр, определяющая, следует ли включать
            конкретное сообщение ассистента в группу.

        Для каждой группы G = [u_1, ..., u_k] вычисляется диапазон индексов
        [group_start, group_end] в session_messages, затем внутри этого диапазона
        формируется последовательность индексов сообщений группы:

            - все user-сообщения из G включаются обязательно;
            - каждое сообщение ассистента внутри диапазона перед включением
            проверяется функцией is_assistant_useful.

        Для фильтрации ассистентского сообщения A_j используются:
            - prev_user_text: текст ближайшего предыдущего сообщения пользователя
            из данной группы (processed_text, если есть, иначе text);
            - next_user_text: текст ближайшего следующего сообщения пользователя
            из данной группы (processed_text, если есть, иначе text).

        :param session_messages: Список сообщений одной сессии диалога.
        :type session_messages: List[Dict[str, Any]]
        :param user_groups: Список групп пользовательских сообщений, каждая группа
            представлена списком индексов user-сообщений.
        :type user_groups: List[List[int]]
        :param is_assistant_useful: Функция-фильтр для ассистентских сообщений.
        :type is_assistant_useful: AssistantMessageFilter
        :return: Список групп сообщений, где каждая группа — это список индексов
            сообщений (user + выбранные assistant) в session_messages.
        :rtype: List[List[int]]
        """
        message_groups: List[List[int]] = []
        n_messages = len(session_messages)

        for group_idx, user_indices in enumerate(user_groups):
            if not user_indices:
                message_groups.append([])
                continue

            user_indices_sorted = sorted(user_indices)
            first_user_idx = user_indices_sorted[0]

            # Определяем правую границу диапазона группы.
            if group_idx + 1 < len(user_groups):
                next_group_first_user = sorted(user_groups[group_idx + 1])[0]
                group_end_idx = max(first_user_idx, next_group_first_user - 1)
            else:
                group_end_idx = n_messages - 1

            group_start_idx = first_user_idx

            # Для удобства заранее отсортированный список индексов пользователя внутри данной группы будем использовать для поиска соседей.
            group_user_set = set(user_indices_sorted)

            def _get_user_text(idx: Optional[int]) -> Optional[str]:
                if idx is None:
                    return ""
                msg = session_messages[idx]
                return msg.get("processed_text") or msg.get("text") or ""

            # Строим последовательность индексов группы в хронологическом порядке.
            group_message_indices: List[int] = []

            for msg_idx in range(group_start_idx, group_end_idx + 1):
                msg = session_messages[msg_idx]
                speaker = msg.get("speaker")

                if speaker == "user":
                    # Включаем только те user-сообщения, которые принадлежат данной группе.
                    if msg_idx in group_user_set:
                        group_message_indices.append(msg_idx)
                elif speaker == "assistant":
                    # Определяем ближайшие user-сообщения до и после msg_idx в рамках группы.
                    prev_user_idx = max(
                        (u for u in user_indices_sorted if u < msg_idx),
                        default=None,
                    )
                    next_user_idx = min(
                        (u for u in user_indices_sorted if u > msg_idx),
                        default=None,
                    )

                    assistant_text = msg.get("processed_text") or msg.get("text") or ""
                    prev_user_text = _get_user_text(prev_user_idx)
                    next_user_text = _get_user_text(next_user_idx)

                    is_assistant_useful = self.assistant_useful_clf.perform(assistant_text, prev_user_text, next_user_text)

                    if is_assistant_useful:
                        group_message_indices.append(msg_idx)
                else:
                    # На данном этапе другие типы сообщений не рассматриваются.
                    continue

            message_groups.append(group_message_indices)

        return message_groups

