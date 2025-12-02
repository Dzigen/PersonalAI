from typing import Union, Dict
from abc import ABC, abstractmethod
from dataclasses import fields

from .CacheKV import CacheKV
from ..task_solver import AgentTaskSolver
from ...pipelines.utils import BaseStages, BaseTaskSolvers


class AbstractCacheOperations(ABC):
    """Абстрактный базовый класс для операций с кешем.

    Класс задаёт интерфейс для получения статистики по кешу
    и очистки связанных key-value-хранилищ. Конкретные реализации
    должны определять структуру stages и tasks_solvers.

    :param tasks_solvers: Набор task-солверов, для которых может вестись кеширование результатов. Значение по умолчанию None.
    :type tasks_solvers: Union[None, BaseTaskSolvers]
    :param stages: Набор стадий пайплайна, каждая из которых может иметь собственный кеш.. Значение по умолчанию None.
    :type stages: Union[None, BaseStages]
    :param cachekv: Интерфейс для работы с основным key-value-кешем текущего объекта.. Значение по умолчанию None.
    :type cachekv: Union[None, CacheKV]
    """
    tasks_solvers: Union[None, BaseTaskSolvers] = None
    stages: Union[None, BaseStages] = None
    cachekv: Union[None, CacheKV] = None

    @abstractmethod
    def get_cache_stat(self) -> Dict[str, Union[None, Dict]]:
        """Метод предназначен для получения статистической информации по кешу.

        :return: Словарь, в котором ключи соответствуют названиям компонент/стадий, а значения содержат статистику по их кешу, либо None, если кеш отсутствует.
        :rtype: Dict[str, Union[None, Dict]]
        """
        pass

    @abstractmethod
    def clear_kv_caches(self, clear_traversal_cache: bool, clear_retrieval_cache: bool) -> None:
        """Метод предназначен для очистки связанных key-value-кешей.

        :param clear_traversal_cache: Флаг, указывающий, требуется ли дополнительно очистить кеш, связанный с traversal-методами.
        :type clear_traversal_cache: bool
        :param clear_retrieval_cache: Флаг, указывающий, требуется ли очистить кеш, связанный с retrieval-операциями.
        :type clear_retrieval_cache: bool
        """
        pass


class CacheOperations(AbstractCacheOperations):
    """Базовая реализация операций с кешем для компонент пайплайна.

    Класс реализует общий механизм:
    - получения статистики по кешам текущего объекта, его стадий и связанных task-солверов;
    - каскадной очистки key-value-кешей.
    """

    def get_cache_stat(self, get_traversal_cache: bool = True) -> Dict[str, Union[None, Dict]]:
        """Метод предназначен для получения статистики по кешу текущей компоненты, а также кешей её стадий и task-солверов.

        :param get_traversal_cache: Если True, то для стадий, реализующих TraversalMethodCacheOpearions, дополнительно будет запрошена статистика. Значение по умолчанию True.
        :type get_traversal_cache: bool
        :return: Словарь со статистикой по кешу. Ключ для текущего класса — имя класса; ключи для стадий и task-солверов — имена их полей в соответствующих dataclass-структурах.
        :rtype: Dict[str, Union[None, Dict]]
        """
        cache_info = dict()
        child_class_name = self.__class__.__name__
        cache_info[child_class_name] = None if self.cachekv is None else self.cachekv.count_items()

        if self.tasks_solvers is not None:
            for field in fields(self.tasks_solvers):
                task_solver: AgentTaskSolver = getattr(self.tasks_solvers, field.name)
                if task_solver.cachekv is not None:
                    cache_info[field.name] = task_solver.cachekv.count_items()
                else:
                    cache_info[field.name] = None

        if self.stages is not None:
            for field in fields(self.stages):
                stage: Union[None, CacheOperations, TraversalMethodCacheOpearions] = \
                    getattr(self.stages, field.name)
                cur_cache = None
                if stage is not None:
                    if isinstance(stage, TraversalMethodCacheOpearions):
                        traversal_method = stage.__class__.__name__
                        cur_cache: Dict[str, Dict] = dict()
                        cur_cache[traversal_method] = stage.get_cache_stat()
                        if get_traversal_cache:
                            cur_cache[traversal_method].update({'traversal_cache': stage.get_traversal_cache()})
                    else:
                        cur_cache = stage.get_cache_stat()

                cache_info[field.name] = cur_cache

        return cache_info

    def clear_kv_caches(self, clear_traversal_cache: bool = False, clear_retrieval_cache: bool = False) -> None:
        """Метод предназначен для каскадной очистки key-value-кешей текущей компоненты, а также связанных стадий и task-солверов.

        :param clear_traversal_cache: Если True, то для стадий, реализующих TraversalMethodCacheOpearions, будет вызван метод clear_traversal_cache(). Значение по умолчанию False.
        :type clear_traversal_cache: bool
        :param clear_retrieval_cache: Если True, то для стадий, реализующих TraversalMethodCacheOpearions, дополнительно будет очищен retrieval-кеш. Значение по умолчанию False.
        :type clear_retrieval_cache: bool
        """
        if self.cachekv is not None:
            self.cachekv.clear()

        if self.stages is not None:
            for field in fields(self.stages):
                stage: Union[None, CacheOperations, TraversalMethodCacheOpearions] = \
                    getattr(self.stages, field.name)

                if stage is not None:

                    if isinstance(stage, TraversalMethodCacheOpearions):
                        if clear_traversal_cache:
                            stage.clear_traversal_cache()
                        if clear_retrieval_cache:
                            stage.clear_kv_caches(clear_traversal_cache, clear_retrieval_cache)
                    else:
                        stage.clear_kv_caches(clear_traversal_cache, clear_retrieval_cache)

        if self.tasks_solvers is not None:
            for field in fields(self.tasks_solvers):
                task_solver: AgentTaskSolver = getattr(self.tasks_solvers, field.name)
                if task_solver.cachekv is not None:
                    task_solver.cachekv.clear()


class TraversalMethodCacheOpearions(CacheOperations):
    """Базовый класс для стадий, в которых помимо key-value-кеша используется дополнительный кеш, связанный с traversal-методами.

    Наследуется от CacheOperations и расширяется интерфейс методами очистки и получения traversal-кеша.
    """
    @abstractmethod
    def clear_traversal_cache(self):
        """Метод предназначен для очистки кеша, связанного с traversal-методами."""
        pass

    @abstractmethod
    def get_traversal_cache(self):
        """Метод предназначен для получения статистики по кешу, связанному с traversal-методами."""
        pass
