from typing import Union, Dict
from abc import ABC, abstractmethod
from dataclasses import fields

from .CacheKV import CacheKV
from ..task_solver import AgentTaskSolver
from ...pipelines.utils import BaseStages, BaseTaskSolvers
from ...pipelines.qa.kg_reasoning.weak_reasoner.knowledge_retriever.utils import AbstractTripletsRetriever


class TraversalMethodCacheOpearions(ABC):

    @abstractmethod
    def clear_traversal_cache(self):
        pass

    @abstractmethod
    def get_traversal_cache(self):
        pass


class AbstractCacheOperations(ABC):
    tasks_solvers: Union[None, BaseTaskSolvers] = None
    stages: Union[None, BaseStages] = None
    cachekv: Union[None, CacheKV] = None

    @abstractmethod
    def get_cache_stat(self) -> Dict[str, Union[None, Dict]]:
        pass

    @abstractmethod
    def clear_kv_caches(self, level: str = 'all') -> None:
        pass


class CacheOperations(AbstractCacheOperations):

    def get_cache_stat(self, get_traversal_cache: bool = True) -> Dict[str, Union[None, Dict]]:
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
                    if issubclass(type(stage), AbstractTripletsRetriever):
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
        if self.cachekv is not None:
            self.cachekv.clear()

        if self.stages is not None:
            for field in fields(self.stages):
                stage: Union[None, CacheOperations, TraversalMethodCacheOpearions] = \
                    getattr(self.stages, field.name)
                
                if stage is not None:
                    
                    if issubclass(type(stage), AbstractTripletsRetriever):
                        if clear_traversal_cache:
                            stage.clear_traversal_cache()
                        if clear_retrieval_cache:
                            stage.clear_kv_caches()
                    else:
                        stage.clear_kv_caches()

        if self.tasks_solvers is not None:
            for field in fields(self.tasks_solvers):
                task_solver: AgentTaskSolver = getattr(self.tasks_solvers, field.name)
                if task_solver.cachekv is not None:
                    task_solver.cachekv.clear()
