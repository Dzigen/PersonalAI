from typing import Union, Dict
from dataclasses import fields
from abc import ABC, abstractmethod
from ...pipelines.utils import BaseStages, BaseTaskSolvers
from ..task_solver import AgentTaskSolver


class AbstractAgentStatOperations(ABC):
    """Абстрактный базовый класс для операций над статистикой LLM-агента
    на уровне пайплайна.

    Определяет интерфейс для:
     - получения агрегированной статистики по стадиям и task-солверам;
     - рекурсивной очистки накопленной статистики.

    :param tasks_solvers: Набор task-солверов, для которых может вестись сбор статистики. Значение по умолчанию None.
    :type tasks_solvers: Union[None, BaseTaskSolvers]
    :param stages: Набор стадий пайплайна, каждая из которых может накапливать собственную статистику. Значение по умолчанию None.
    :type stages: Union[None, BaseStages]
    """
    tasks_solvers: Union[None, BaseTaskSolvers] = None
    stages: Union[None, BaseStages] = None

    @abstractmethod
    def get_agent_tgen_stat(self) -> Dict[str, Union[None, Dict]]:
        pass

    @abstractmethod
    def clear_agent_tgen_stat(self) -> None:
        pass


class AgentStatOperations(AbstractAgentStatOperations):
    """Реализация операций над статистикой LLM-агента для составных компонент.

    Рекурсивно обходит:
     - дочерние стадии (stages), реализующие AbstractAgentStatOperations;
     - task-солверы (tasks_solvers) с настроенным кешем статистики inference,
    и делегирует им расчёт/очистку статистики.
    """

    def get_agent_tgen_stat(self) -> Dict[str, Union[None, Dict]]:
        """Метод предназначен для получения статистической информации по генерации по дочерним стадиям и task-солверам.

        :return: Словарь, в котором ключи соответствуют названиям компонент/стадий, а значения - словари метрик, либо None, если статистика для компоненты не ведется.
        :rtype: Dict[str, Union[None, Dict]]
        """
        cache_info = dict()

        if self.stages is not None:
            for field in fields(self.stages):
                stage: Union[object, None, AbstractAgentStatOperations] = getattr(self.stages, field.name)
                if (stage is not None) and issubclass(type(stage), AbstractAgentStatOperations):
                    cache_info[field.name] = stage.get_agent_tgen_stat()

        if self.tasks_solvers is not None:
            for field in fields(self.tasks_solvers):
                task_solver: AgentTaskSolver = getattr(self.tasks_solvers, field.name)
                if task_solver.inference_stat_cache is not None:
                    cache_info[field.name] = task_solver.inference_stat_cache.calculate_stat()
                else:
                    cache_info[field.name] = None

        return cache_info

    def clear_agent_tgen_stat(self) -> None:
        """Рекурсивно очищает кеш статистики генерации по всем вложенным стадиям и task-солверам, у которых настроен кеш статистики."""
        if self.stages is not None:
            for field in fields(self.stages):
                stage: Union[object, None, AbstractAgentStatOperations] = getattr(self.stages, field.name)
                if (stage is not None) and (issubclass(type(stage), AbstractAgentStatOperations)):
                    stage.clear_agent_tgen_stat()

        if self.tasks_solvers is not None:
            for field in fields(self.tasks_solvers):
                task: AgentTaskSolver = getattr(self.tasks_solvers, field.name)
                if task.inference_stat_cache is not None:
                    task.inference_stat_cache.clear()
