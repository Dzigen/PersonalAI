from dataclasses import dataclass, fields
from typing import Tuple, Dict, Union
import json
from copy import deepcopy
import hashlib
from abc import ABC, abstractmethod

from .language_detector import detect_lang
from .errors import ReturnStatus, STATUS_MESSAGE
from .cache_kv import CacheKV
from .tracing import accumulate_tasksolver_info
from .agent_stat_analyzer import AgentStatAnalyzerConfig, AgentStatAnalyzer
from ..agents.utils import AbstractAgentConnector
from ..db_drivers.kv_driver import KeyValueDriverConfig
from .data_structs import BaseConfigOperations
from .data_structs import LoggingConfig, LogLevel, Logger


@dataclass
class AgentTaskSuite:
    """Набор гиперпараметров для инференса и разбора ответа LLM-агента в рамках заданной атомарной задачи.

    :param system_prompt: System-промпт с описанием персоны, свойствам которой должен удовлетворять LLM-агент во время инференса.
    :type system_prompt: str
    :param user_prompt: User-промпт для инференса LLM-агента с описанием задачи.
    :type user_prompt: str
    :param assistant_prompt: Assistant-промпт с дополнительной информацией по решаемой задаче для инференса LLM-агента.
    :type assistant_prompt: str
    :param parse_answer_func: Кастомная функция, которая должна выполнять промежуточный разбор ответа LLM-агента, полученного в рамках инференса.
    :type parse_answer_func: object
    """
    system_prompt: str
    user_prompt: str
    assistant_prompt: str
    parse_answer_func: object


@dataclass
class AgentTaskSolverConfig(LoggingConfig):
    """Конфигурация agent-солвера.

    :param version: Версия набора промптов/парсеров для решения некоторой LLM-задачи.
    :type version: str
    :param suites: Набор гиперпараметров для инференса и разбора ответа LLM-агента в рамках заданной атомарной задачи.
    :type suites: Dict[str, AgentTaskSuite]
    :param formate_context_func: Кастомная функция, приводящая входной (в agent-солвер) набор данных в строковый формат (в виде словаря со строковыми значениями), который далее будет добавляться в user-prompt для LLM-агента.
    :type formate_context_func: object
    :param postprocess_answer_func: Кастомная функция, приводящая разобранный ответ от LLM-агента к формату, который требуется для данной атомарной задачи.
    :type postprocess_answer_func: object
    :param cache_table_name: Название таблицы в структуре (базе) данных, куда будут сохраняться (кешироваться) основные результаты работы AgentTaskSolver-класса.
    :type cache_table_name: str
    :param inferencestat_table_name: Название таблицы в структуре (базе) данных, куда будут сохраняться мета-информация/статистика по inference-операции.
    :type inferencestat_table_name: str
    """
    version: str
    suites: Dict[str, AgentTaskSuite]
    formate_context_func: object
    postprocess_answer_func: object

    cache_table_name: str
    inferencestat_table_name: str


class AgentTaskSolver:
    """Класс-обёртка, предназначенный для решения атомарной задачи на базе inference-операции LLM-агента.

    :param agent: Интерфейс взаимодействия с LLM-агентом.
    :type agent: AbstractAgentConnector
    :param config: Конфигурация решения конкретной атомарной задачи.
    :type config: AgentTaskSolverConfig
    :param cache_kvdriver_config: Конфигурация структуры данных для кеширования результатов inference-операции. Значение по умолчанию None.
    :type cache_kvdriver_config: Union[None, KeyValueDriverConfig], optional
    :param inferencestat_config: Конфигурация компоненты для сбора информации и расчёта статистик по результатам выполнения inference-операций в рамках заданной LLM-задачи. Значение по умолчанию None.
    :type inferencestat_config: Union[None, AgentStatAnalyzerConfig], optional
    """
    cachekv: CacheKV
    inference_stat_cache: AgentStatAnalyzer

    def __init__(self, agent: AbstractAgentConnector, config: AgentTaskSolverConfig,
                 cache_kvdriver_config: Union[None, KeyValueDriverConfig] = None,
                 inferencestat_config: Union[None, AgentStatAnalyzerConfig] = None) -> None:
        self.config = config
        self.agent = agent

        if cache_kvdriver_config is not None and self.config.cache_table_name is not None:
            cache_config = deepcopy(cache_kvdriver_config)
            cache_config.db_config.db_info['table'] = self.config.cache_table_name
            self.cachekv = CacheKV(cache_config)
        else:
            self.cachekv = None

        # print(self.config.cache_table_name, inferencestat_config is not None, self.config.inferencestat_table_name is not None)
        if inferencestat_config is not None and self.config.inferencestat_table_name is not None:
            astat_config = deepcopy(inferencestat_config)
            astat_config.table_driver_config.db_config.db_info['table'] = self.config.inferencestat_table_name
            self.inference_stat_cache = AgentStatAnalyzer(astat_config)
        else:
            self.inference_stat_cache = None

        self.log = Logger(self.config.log_path)
        self.verbose = self.config.verbose
        self.log_level = self.config.log_level

    @accumulate_tasksolver_info
    def solve(self, lang: str = 'en', gen_strategy: Union[None, Dict[str, str]] = None, **kwargs) -> Tuple[object, ReturnStatus, bool]:
        """Метод предназначен для запуска agent-солвера на заданных входных данных.

        :param lang: Язык промптов, которые будут использоваться на этапе инференса LLM-агента. Значение по умолчанию 'en'.
        :type lang: str, optional
        :param gen_strategy: Стратегия генерации текста для используемого LLM-агента. В случае None-значение будет использоваться стратегия по умолчанию. Значение по умолчанию None.
        :type gen_strategy: Union[None, Dict[str, str]], optional
        :return: Кортеж из трёх объектов: (1) результат работы agent-солвера; (2) статус завершения операции с пояснительной информацией; (3) True, если результат генерации был получен из кеша (cache hit), иначе был выполнен инференс LLM-для решения задачи (cache miss).
        :rtype: Tuple[object, ReturnStatus]
        """
        task_result, status, cache_hit = None, ReturnStatus.success, False
        self.log.debug("=" * 20, verbose=self.verbose, log_level=self.log_level)
        self.log.debug("1. Предобработка данных для их дальнейшней вставки в user-prompt...", verbose=self.verbose, log_level=self.log_level)

        try:
            formated_context = self.config.formate_context_func(**kwargs)
        except Exception as e:
            self.log.error(str(e), verbose=self.verbose, log_level=self.log_level)
            status = ReturnStatus.bad_formater
        else:
            self.log.debug("Результат:\n %s", json.dumps(formated_context, indent=1, ensure_ascii=False), verbose=self.verbose, log_level=self.log_level)
        finally:
            self.log.debug(f"Статус: %s .", STATUS_MESSAGE[status], verbose=self.verbose, log_level=self.log_level)

        # Если удалось без ошибок привести данные в формат контекста
        # для вставки в user-prompt
        if status == ReturnStatus.success:
            self.log.debug("-" * 20, verbose=self.verbose, log_level=self.log_level)
            self.log.debug("2. Детекция используемого языка...", verbose=self.verbose, log_level=self.log_level)
            flatten_context = ', '.join(list(formated_context.values()))

            detected_lang, raw_lang, status = detect_lang(
                flatten_context) if lang == 'auto' else (lang, lang, ReturnStatus.success)

            self.log.debug("Результат: %s", detected_lang, verbose=self.verbose, log_level=self.log_level)
            self.log.debug("Статус: %s , %s .", STATUS_MESSAGE[status], raw_lang, verbose=self.verbose, log_level=self.log_level)

        # Если удалось определить язык (распознанный язык находится в списке доступных)
        if status == ReturnStatus.success:
            self.log.debug("-" * 20, verbose=self.verbose, log_level=self.log_level)
            self.log.debug("3. Добавление информации в user-prompt...", verbose=self.verbose, log_level=self.log_level)
            try:
                enriched_user_prompt = self.config.suites[detected_lang].user_prompt.format(
                    **formated_context)
            except Exception as e:
                self.log.error(str(e), verbose=self.verbose, log_level=self.log_level)
                status = ReturnStatus.bad_user_prompt_maping
            else:
                self.log.debug("Результат:\n %s .", enriched_user_prompt, verbose=self.verbose, log_level=self.log_level)
            finally:
                self.log.debug("Статус: %s", STATUS_MESSAGE[status], verbose=self.verbose, log_level=self.log_level)

        # Если удалось добавить дополнительную инофрмацию в user-prompt
        if status == ReturnStatus.success:
            self.log.debug("-" * 20, verbose=self.verbose, log_level=self.log_level)
            self.log.debug("4. Генерация ответа с помощью LLM-агента.", verbose=self.verbose, log_level=self.log_level)

            raw_answer = None

            # preparing cache key
            gen_strategy = self.agent.config.gen_strategy if gen_strategy is None else gen_strategy
            str_genstrat = ";".join(list(map(lambda p: f"{p[0]}={p[1]}", sorted(
                [(k, str(v)) for k, v in gen_strategy.items()], key=lambda p: p[0]))))
            str_creds = ";".join(list(map(lambda p: f"{p[0]}={p[1]}", sorted(
                [(k, str(v)) for k, v in self.agent.config.credentials.items()], key=lambda p: p[0]))))
            sprompt_hash = hashlib.sha1(self.config.suites[detected_lang].system_prompt.encode()).hexdigest()
            uprompt_hash = hashlib.sha1(enriched_user_prompt.encode()).hexdigest()
            if self.config.suites[detected_lang].assistant_prompt is None:
                aprompt_hash = hashlib.sha1("__<|None|>__".encode()).hexdigest()
            else:
                aprompt_hash = hashlib.sha1(
                    self.config.suites[detected_lang].assistant_prompt.encode()).hexdigest()
            cache_key = [sprompt_hash, uprompt_hash, aprompt_hash, str_genstrat, str_creds]

            key_hash = None

            if self.cachekv is not None:
                self.log.debug("Поиск ответа в кеше...", verbose=self.verbose, log_level=self.log_level)
                cstatus, key_hash, cached_result = self.cachekv.load_value(
                    key=cache_key)
                if cstatus == 0:
                    self.log.debug("Результат по заданной конфигурации гиперпараметров уже был получен.", verbose=self.verbose, log_level=self.log_level)
                    self.log.debug("* cache table_name: %s", self.cachekv.kv_conn.config.db_info['table'], verbose=self.verbose, log_level=self.log_level)
                    self.log.debug("* cahce hash_key: %s .", key_hash, verbose=self.verbose, log_level=self.log_level)
                    formated_log_cachekey = '\n-'.join(cache_key)
                    self.log.debug("* hash seed: %s .", formated_log_cachekey, verbose=self.verbose, log_level=self.log_level)

                    cache_hit = True
                    raw_answer = cached_result
                else:
                    self.log.debug("Результата по заданной конфигурации гиперпараметров в кеше нет.", verbose=self.verbose, log_level=self.log_level)
                    self.log.debug("* cache table_name: %s", self.cachekv.kv_conn.config.db_info['table'], verbose=self.verbose, log_level=self.log_level)
                    self.log.debug("* cache hash_key: %s .", key_hash, verbose=self.verbose, log_level=self.log_level)
                    formated_log_cachekey = '\n-'.join(cache_key)
                    self.log.debug("* hash seed: %s .", formated_log_cachekey, verbose=self.verbose, log_level=self.log_level)

            if not cache_hit:
                self.log.debug("Выполняем инференс llm...", verbose=self.verbose, log_level=self.log_level)

                raw_answer, inference_info = self.agent.generate(
                    system_prompt=self.config.suites[detected_lang].system_prompt,
                    user_prompt=enriched_user_prompt,
                    assistant_prompt=self.config.suites[detected_lang].assistant_prompt,
                    gen_strategy=gen_strategy)

                if self.inference_stat_cache is not None:
                    self.inference_stat_cache.add_values([inference_info])

                if self.cachekv is not None:
                    self.log.debug("Кешируем полученный результат.", verbose=self.verbose, log_level=self.log_level)
                    self.cachekv.save_value(value=raw_answer, key_hash=key_hash)

            self.log.debug("Результат:\n%s", raw_answer, verbose=self.verbose, log_level=self.log_level)
            self.log.debug("Статус: %s .", STATUS_MESSAGE[status], verbose=self.verbose, log_level=self.log_level)

        # Если сгенрированная raw-строка не является пустой
        if status == ReturnStatus.success:
            self.log.debug("-" * 20, verbose=self.verbose, log_level=self.log_level)
            self.log.debug("5. Разбор ответа, сгенерированного LLM-агентом.", verbose=self.verbose, log_level=self.log_level)

            try:
                formated_answer = self.config.suites[detected_lang].parse_answer_func(
                    raw_answer, **kwargs)
            except (KeyError, ValueError) as e:
                self.log.error(str(e), verbose=self.verbose, log_level=self.log_level)
                status = ReturnStatus.bad_parser
            else:
                self.log.debug("Результат:\n%s", formated_answer, verbose=self.verbose, log_level=self.log_level)
            finally:
                self.log.debug("Статус: %s .", STATUS_MESSAGE[status], verbose=self.verbose, log_level=self.log_level)

        #  Если не было ошибок при разборе raw-строки
        if status == ReturnStatus.success:
            self.log.debug("-" * 20, verbose=self.verbose, log_level=self.log_level)
            self.log.debug("6. Постобработка ответа от LLM-агента.", verbose=self.verbose, log_level=self.log_level)

            try:
                task_result = self.config.postprocess_answer_func(formated_answer, **kwargs)
            except Exception as e:
                self.log.error(str(e), verbose=self.verbose, log_level=self.log_level)
                status = ReturnStatus.bad_postprocessor
            else:
                self.log.debug("Результат:\n%s", task_result, verbose=self.verbose, log_level=self.log_level)
            finally:
                self.log.debug("Статус: %s .", STATUS_MESSAGE[status], verbose=self.verbose, log_level=self.log_level)

        return task_result, status, cache_hit


@dataclass
class AgentTaskBaseConfig:
    """Базовый класс конфигурации для agent-солверов.

    :param suites: Набор гиперпараметров для инференса и разбора ответа LLM-агента
        по поддерживаемым языкам (ключ — код языка).
    :type suites: Dict[str, AgentTaskSuite]
    :param custom_formate: Кастомная функция, приводящая входные данные к формату,
        ожидаемому конкретным task-конвейером.
    :type custom_formate: object
    """
    suites: Dict[str, AgentTaskSuite]
    custom_formate: object


class BaseAgentTaskConfigSelector(ABC):
    @staticmethod
    @abstractmethod
    def get_available_configs() -> None:
        pass

    @staticmethod
    @abstractmethod
    def select(base_config_version: str, cache_table_name: str, inferencestat_table_name: str,
               verbose: bool = False, log_level: LogLevel = LogLevel.DISABLED) -> AgentTaskSolverConfig:
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

    def versions_to_configs(self, verbose: bool = False, log_level: LogLevel = LogLevel.DISABLED):
        fields_iterator = fields(self)
        for field_object in fields_iterator:
            if field_object.name == 'task_to_selector_mapping':
                continue

            field_value = getattr(self, field_object.name)

            if isinstance(field_value, str):
                task_config_version = field_value
                agent_task_config = self.task_to_selector_mapping[field_object.name].select(
                    base_config_version=task_config_version, verbose=verbose, log_level=log_level)
                setattr(self, field_object.name, agent_task_config)
