from enum import Enum
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from collections import defaultdict
from typing import List, Tuple, Dict, Union
from time import time
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


@dataclass
class SimpleModuleResult(ModuleResult):
    pass


@dataclass
class CompositeModuleSummaryResult(ModuleResult):
    pass


@dataclass
class BaseCompositeModuleDetailedResult(ABC):
    stages: Dict[str, List[object]] = field(default_factory=lambda: defaultdict(list))
    steps: Dict[str, List[object]] = field(default_factory=lambda: defaultdict(list))
    task_solvers: Dict[str, List[object]] = field(default_factory=lambda: defaultdict(list))
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
    def get_results_sequence(self) -> List[Tuple[ModuleType, ModuleResult]]:
        pass

    def add(self, module_name: str, module_type: ModuleType, module_result: Union[CompositeModuleResult, SimpleModuleResult]):
        pass


def accumulate_tasksolver_info(func):
    def wrapper(*args, **kwargs) -> Tuple[object, ReturnStatus, SimpleModuleResult]:
        s_time = time()
        result, status = func(*args, **kwargs)
        e_time = time()

        trace = SimpleModuleResult(
            context=kwargs,
            result=result,
            status=status,
            elapsed_time=round(e_time - s_time, 5)
        )
        trace.context['positional_arguments'] = args

        return result, trace
    return wrapper


def accumulate_step_info(func):
    def wrapper(*args, **kwargs) -> Tuple[object, SimpleModuleResult]:
        s_time = time()
        result = func(*args, **kwargs)
        e_time = time()

        trace = SimpleModuleResult(
            context=kwargs,
            result=result,
            elapsed_time=round(e_time - s_time, 5)
        )
        trace.context['positional_arguments'] = args

        return result, trace
    return wrapper


def accumulate_stage_info(func):
    def wrapper(*args, **kwargs) -> Tuple[object, ReturnInfo, CompositeModuleResult]:
        s_time = time()
        result, rinfo, intermediate_trace = func(*args, **kwargs)
        e_time = time()

        stage_summary = CompositeModuleSummaryResult(
            context=kwargs,
            result=result,
            status=rinfo.status,
            intermediate_results=intermediate_trace,
            elapsed_time=round(e_time - s_time, 5)
        )
        stage_summary.context['positional_arguments'] = args

        trace = CompositeModuleResult(
            summary=stage_summary,
            detailed_result=intermediate_trace
        )

        return result, rinfo, trace
    return wrapper
