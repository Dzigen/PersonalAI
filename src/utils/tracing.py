from enum import Enum
from dataclasses import dataclass, field, asdict
from abc import ABC, abstractmethod
from copy import deepcopy
import os
from collections import defaultdict
from typing import List, Tuple, Dict, Union
from time import time
import json

from ..utils.errors import ReturnInfo, ReturnStatus


class ModuleType(Enum):
    stage = 'stage'
    task_solver = 'task_solver'
    step = 'step'


@dataclass
class ModuleResult:
    context: Dict[str, object]
    result: object
    status: Union[None, ReturnStatus] = None
    elapsed_time: Union[None, float] = None  # seconds
    cache_hit: Union[None, bool] = None


@dataclass
class SimpleModuleResult(ModuleResult):
    pass


@dataclass
class CompositeModuleSummaryResult(ModuleResult):
    pass


@dataclass
class BaseCompositeModuleDetailedResult(ABC):
    modules_categories: Dict[ModuleType, Dict[str, Union[SimpleModuleResult, object]]] = field(default_factory=lambda: {
        ModuleType.stage: defaultdict(list), ModuleType.step: defaultdict(list), ModuleType.task_solver: defaultdict(list)})
    execution_sequence: List[Tuple[ModuleType, str]] = field(default_factory=lambda: list())

    @abstractmethod
    def get_results_sequence(self) -> List[Tuple[ModuleType, ModuleResult]]:
        pass

    @abstractmethod
    def add(self, module_name: str, module_type: ModuleType, module_result: Union[SimpleModuleResult, object]):
        pass


@dataclass
class CompositeModuleResult:
    summary: CompositeModuleSummaryResult
    detailed_result: BaseCompositeModuleDetailedResult


@dataclass
class CompositeModuleDetailedResult(BaseCompositeModuleDetailedResult):
    def get_results_sequence(self) -> List[Tuple[ModuleType, str, ModuleResult]]:
        sequence = []
        categories_pointer = {ModuleType.stage: defaultdict(lambda: 0), ModuleType.step: defaultdict(lambda: 0), ModuleType.task_solver: defaultdict(lambda: 0)}
        for module_info in self.execution_sequence:
            cur_pointer = categories_pointer[module_info[0]][module_info[1]]

            cur_trace = self.modules_categories[module_info[0]][module_info[1]][cur_pointer]
            if isinstance(cur_trace, CompositeModuleResult):
                cur_trace = cur_trace.summary

            sequence.append((module_info[0], module_info[1], cur_trace))

            categories_pointer[module_info[0]][module_info[1]] += 1
        return sequence

    def add(self, module_name: str, module_type: ModuleType, module_result: Union[CompositeModuleResult, SimpleModuleResult]):
        self.execution_sequence.append((module_type, module_name))
        self.modules_categories[module_type][module_name].append(deepcopy(module_result))


def accumulate_tasksolver_info(func):
    def wrapper(*args, **kwargs) -> Tuple[object, ReturnStatus, SimpleModuleResult]:
        s_time = time()
        result, status, cache_hit = func(*args, **kwargs)
        e_time = time()

        trace = SimpleModuleResult(
            context=deepcopy(kwargs),
            result=deepcopy(result),
            status=status,
            elapsed_time=round(e_time - s_time, 5),
            cache_hit=cache_hit
        )
        trace.context['positional_arguments'] = deepcopy(args[1:])  # исключаем self

        return result, status, trace
    return wrapper


def accumulate_step_info(func):
    def wrapper(*args, **kwargs) -> Tuple[object, SimpleModuleResult]:
        s_time = time()
        result, rinfo, cache_hit = func(*args, **kwargs)
        e_time = time()

        trace = SimpleModuleResult(
            context=deepcopy(kwargs),
            result=deepcopy(result),
            elapsed_time=round(e_time - s_time, 5),
            cache_hit=cache_hit,
            status=rinfo.status
        )
        trace.context['positional_arguments'] = deepcopy(args[1:])  # исключаем self

        return result, rinfo, trace
    return wrapper


def accumulate_stage_info(func):
    def wrapper(*args, **kwargs) -> Tuple[object, ReturnInfo, CompositeModuleResult]:
        s_time = time()
        result, rinfo, intermediate_trace, cache_hit = func(*args, **kwargs)
        e_time = time()

        stage_summary = CompositeModuleSummaryResult(
            context=deepcopy(kwargs),
            result=deepcopy(result),
            status=rinfo.status,
            elapsed_time=round(e_time - s_time, 5),
            cache_hit=cache_hit
        )
        stage_summary.context['positional_arguments'] = deepcopy(args[1:])  # исключаем self

        trace = CompositeModuleResult(
            summary=stage_summary,
            detailed_result=intermediate_trace
        )

        return result, rinfo, trace
    return wrapper
