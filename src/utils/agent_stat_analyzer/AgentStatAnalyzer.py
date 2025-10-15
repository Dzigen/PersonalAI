from dataclasses import dataclass, asdict, field
from typing import Dict, Union, List

from ...db_drivers.table_driver.utils import AbstractTableDatabaseConnection, TableDBInstance
from ...db_drivers.table_driver import TableDriverConfig, TableDriver
from .supported_dbvendors import SUPPORTED_VENDORS
from .utils import AbstractTableStatOperations, LLMInferenceStat, CalculateMetrics
from .configs import DEFAULT_AGENTSTAT_TABLEDB_DRIVER_CONFIG


@dataclass
class AgentStatAnalyzerConfig:
    table_driver_config: TableDriverConfig = field(default_factory=lambda: DEFAULT_AGENTSTAT_TABLEDB_DRIVER_CONFIG)
    metrics_info: CalculateMetrics = field(default_factory=lambda: CalculateMetrics())
    column_info: List[str] = field(default_factory=lambda: ['prompt_tokens_amount', 'generated_tokens_amount', 'inference_elapsed_time'])


class AgentStatAnalyzer:
    def __init__(self, config: AgentStatAnalyzerConfig = AgentStatAnalyzerConfig()):
        self.config = config

        self.db_conn: AbstractTableDatabaseConnection = TableDriver.connect(self.config.table_driver_config)
        self.operations: AbstractTableStatOperations = SUPPORTED_VENDORS[self.config.table_driver_config.db_vendor](self.db_conn)

        self.table_operations: Dict[str, object] = {
            'min': self.operations.calculate_min,
            'max': self.operations.calculate_max,
            'mean': self.operations.calculate_mean,
            'median': self.operations.calculate_median,
            'std': self.operations.calculate_std,
            'count': self.operations.count_all_values,
            'count_not_null': self.operations.count_notnull_values,
            'sum': self.operations.calculate_sum
        }

    def calculate_stat(self) -> Dict[str, Dict[str, Union[float, int]]]:
        stats: Dict[str, Dict[str, Union[None, float, int]]] = dict()
        for cname in self.config.column_info:
            tmp_results = dict()
            for metric, need_calculate in asdict(self.config.metrics_info).items():
                if need_calculate:
                    tmp_results[metric] = self.table_operations[metric](cname)
            stats[cname] = tmp_results

        return stats

    def add_values(self, values: List[LLMInferenceStat]) -> List[str]:
        formated_instances = [TableDBInstance(values=value) for value in values]
        self.db_conn.create(formated_instances)
        return [str(inst.id) for inst in formated_instances]
