from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Union

from ..utils import Logger
from ..agents.utils import AbstractAgentConnector
from ..db_drivers.kv_driver import KeyValueDriverConfig
from ..utils.data_structs import BaseComponentConfig, LanguageConfig
from .configs import QP_MAIN_LOG_PATH, DEFAULT_QUEST_PROC_KVCACHE_CONFIG
from ..utils.cache_kv.CacheOperations import CacheOperations

from .utils import Question
from .quest_rephraser import QuestRephraser, QuestRephraserConfig


@dataclass
class QuestProcessorConfig(BaseComponentConfig, LanguageConfig):
    """Конфигурация компоненты обработки вопросов."""

    quest_rephraser_config: Union[Dict, QuestRephraserConfig] = field(
        default_factory=lambda: QuestRephraserConfig())

    log: Logger = field(default_factory=lambda: Logger(QP_MAIN_LOG_PATH))

    def to_str(self):
        # TODO
        raise NotImplementedError

    @staticmethod
    def from_dict(dict_config: Dict):
        dictconfig_copy = deepcopy(dict_config)
        formated_config = QuestProcessorConfig(**dictconfig_copy)
        formated_config.formate_fields()
        return formated_config

    def formate_fields(self):
        if isinstance(self.quest_rephraser_config, dict):
            self.quest_rephraser_config = QuestRephraserConfig.from_dict(self.quest_rephraser_config)
        else:
            self.quest_rephraser_config.formate_fields()


class QuestProcessor(CacheOperations):
    """Класс для обработки вопросов.

    Основная задача данного класса — подготовка вопросов к последующему запуску qa-пайплайна.

    :param questions: Список вопросов, подлежащих обработке.
    :type questions: List[Dict[str, Any]]
    :param agent: Коннектор к конкретному LLM-агенту для выполнения inference-операций.
    :type agent: AbstractAgentConnector
    :param config: Конфигурация конвейера обработки вопросов. По умолчанию используется QuestProcessorConfig() c параметрами по умолчанию.
    :type config: Optional[QuestProcessorConfig], optional
    :param cache_kvdriver_config: Конфигурация структуры данных для кеширования промежуточных результатов в рамках компонент данного класса. Значение по умолчанию None.
    :type cache_kvdriver_config: Union[KeyValueDriverConfig, None], optional
    """

    def __init__(
        self,
        questions: List[Dict[str, Any]],
        agent: AbstractAgentConnector,
        config: Union[Dict, QuestProcessorConfig] = QuestProcessorConfig(),
        cache_kvdriver_config: Union[KeyValueDriverConfig, None] = DEFAULT_QUEST_PROC_KVCACHE_CONFIG
    ) -> None:
        if isinstance(config, dict):
            config: QuestProcessorConfig = QuestProcessorConfig.from_dict(config)
        else:
            config.formate_fields()

        self.config = config

        self.questions: List[Dict[str, Any]] = questions

        self.quest_rephraser: QuestRephraser = QuestRephraser(
            agent, config.quest_rephraser_config, cache_kvdriver_config
        )

        self.log = config.log
        self.verbose = config.verbose


    def run_question_rephrasing(self) -> List[Dict[str, Any]]:
        self.log("START REPHRASING QUESTION...", verbose=self.verbose)
        for question_w_meta in self.questions:
            raw_question_list = question_w_meta.get("qa")

            if not isinstance(raw_question_list, list) or not raw_question_list:
                continue

            question_list: List[Question] = [Question.from_dict(quest) for quest in raw_question_list]

            for question in question_list:

                question_text = question.question
                if not question_text:
                    question.rephrased_question = ''
                    continue

                rephrased_question_text, is_reject_answer = self.quest_rephraser.perform(
                    question=question_text
                )

                question.rephrased_question = rephrased_question_text
                if is_reject_answer:
                    question.was_reject_while_rephrasing = True

            question_w_meta['qa'] = [quest.to_dict() for quest in question_list]

        return self.questions