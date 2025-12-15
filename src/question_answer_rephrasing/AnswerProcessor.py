from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Union

from ..utils import Logger
from ..agents.utils import AbstractAgentConnector
from ..db_drivers.kv_driver import KeyValueDriverConfig
from ..utils.data_structs import BaseComponentConfig, LanguageConfig
from .configs import AP_MAIN_LOG_PATH, DEFAULT_ANSW_PROC_KVCACHE_CONFIG
from ..utils.cache_kv.CacheOperations import CacheOperations

from .utils import Question
from .answ_rephraser import AnswerRephraser, AnswerRephraserConfig


@dataclass
class AnswerProcessorConfig(BaseComponentConfig, LanguageConfig):
    """Конфигурация компоненты обработки ответов."""

    answer_rephraser_config: Union[Dict, AnswerRephraserConfig] = field(
        default_factory=lambda: AnswerRephraserConfig())

    log: Logger = field(default_factory=lambda: Logger(AP_MAIN_LOG_PATH))

    def to_str(self):
        # TODO
        raise NotImplementedError

    @staticmethod
    def from_dict(dict_config: Dict):
        dictconfig_copy = deepcopy(dict_config)
        formated_config = AnswerProcessorConfig(**dictconfig_copy)
        formated_config.formate_fields()
        return formated_config

    def formate_fields(self):
        if isinstance(self.answer_rephraser_config, dict):
            self.answer_rephraser_config = AnswerRephraserConfig.from_dict(self.answer_rephraser_config)
        else:
            self.answer_rephraser_config.formate_fields()


class AnswerProcessor(CacheOperations):
    """Класс для обработки ответов.

    Основная задача данного класса — подготовка ответов к сравнению с исходными gold-ответами.

    :param questions_w_answs: Список вопросов, после обработки с ответами на них.
    :type questions: List[Dict[str, Any]]
    :param agent: Коннектор к конкретному LLM-агенту для выполнения inference-операций.
    :type agent: AbstractAgentConnector
    :param config: Конфигурация конвейера обработки вопросов. По умолчанию используется AnswerProcessorConfig() c параметрами по умолчанию.
    :type config: Optional[AnswerProcessorConfig], optional
    :param cache_kvdriver_config: Конфигурация структуры данных для кеширования промежуточных результатов в рамках компонент данного класса. Значение по умолчанию None.
    :type cache_kvdriver_config: Union[KeyValueDriverConfig, None], optional
    """

    def __init__(
        self,
        questions_w_answs: List[Dict[str, Any]],
        agent: AbstractAgentConnector,
        config: Union[Dict, AnswerProcessorConfig] = AnswerProcessorConfig(),
        cache_kvdriver_config: Union[KeyValueDriverConfig, None] = DEFAULT_ANSW_PROC_KVCACHE_CONFIG
    ) -> None:
        if isinstance(config, dict):
            config: AnswerProcessorConfig = AnswerProcessorConfig.from_dict(config)
        else:
            config.formate_fields()

        self.config = config

        self.questions_w_answs: List[Dict[str, Any]] = questions_w_answs

        self.answer_rephraser: AnswerRephraser = AnswerRephraser(
            agent, config.answer_rephraser_config, cache_kvdriver_config
        )

        self.log = config.log
        self.verbose = config.verbose


    def run_answer_rephrasing(self) -> List[Dict[str, Any]]:
        self.log("START REPHRASING ANSWERS...", verbose=self.verbose)
        for question_w_meta in self.questions_w_answs:
            raw_question_list = question_w_meta.get("qa")

            if not isinstance(raw_question_list, list) or not raw_question_list:
                continue

            question_list: List[Question] = [Question.from_dict(quest) for quest in raw_question_list]

            for question in question_list:

                # Исходный вопрос
                question_text = question.question
                # Перефразированный вопрос
                rephrased_question_text = question.rephrased_question
                # Полученный ответ
                raw_answer_text = question.raw_answer

                if not raw_answer_text:
                    question.rephrased_answer = ''
                    continue

                rephrased_answer_text = self.answer_rephraser.perform(
                    question=question_text,
                    rephrased_question=rephrased_question_text,
                    raw_answer=raw_answer_text
                )

                question.final_answer = rephrased_answer_text

            question_w_meta['qa'] = [quest.to_dict() for quest in question_list]

        return self.questions_w_answs
