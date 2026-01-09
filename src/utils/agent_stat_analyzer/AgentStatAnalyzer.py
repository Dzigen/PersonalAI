from dataclasses import dataclass, asdict, field
from typing import Dict, Union, List
from copy import deepcopy

from ...db_drivers.table_driver.utils import AbstractTableDatabaseConnection, TableDBInstance
from ...db_drivers.table_driver import TableDriverConfig, TableDriver
from .supported_dbvendors import SUPPORTED_VENDORS
from .utils import AbstractTableStatOperations, LLMInferenceStat, CalculateMetrics
from .configs import DEFAULT_AGENTSTAT_TABLEDB_DRIVER_CONFIG
from ..data_structs import BaseConfigOperations


@dataclass
class AgentStatAnalyzerConfig(BaseConfigOperations):
    """Конфигурация компоненты для хранения и анализа статистики LLM-инференса.

    :param table_driver_config: Конфигурация подключения к табличной БД, в которой хранятся записи статистики.
    :type table_driver_config: TableDriverConfig
    :param metrics_info: Набор флагов, определяющих, какие агрегирующие метрики необходимо рассчитывать.
    :type metrics_info: CalculateMetrics
    :param column_info: Список имен столбцов, по которым будут рассчитываться метрики. По умолчанию включает число токенов и время инференса.
    :type column_info: List[str]
    """
    table_driver_config: TableDriverConfig = field(default_factory=lambda: DEFAULT_AGENTSTAT_TABLEDB_DRIVER_CONFIG)
    metrics_info: CalculateMetrics = field(default_factory=lambda: CalculateMetrics())
    column_info: List[str] = field(default_factory=lambda: ['prompt_tokens_amount', 'generated_tokens_amount', 'inference_elapsed_time'])

    def to_str(self):
        # TODO
        raise NotImplementedError

    @staticmethod
    def from_dict(dict_config: Dict):
        dictconfig_copy = deepcopy(dict_config)
        formated_config = AgentStatAnalyzerConfig(**dictconfig_copy)
        formated_config.formate_fields()
        return formated_config

    def formate_fields(self):
        if isinstance(self.table_driver_config, dict):
            self.table_driver_config = TableDriverConfig.from_dict(self.table_driver_config)
        else:
            self.table_driver_config.formate_fields()

        if isinstance(self.metrics_info, dict):
            self.metrics_info = CalculateMetrics(**self.metrics_info)


class AgentStatAnalyzer:
    """Компонента для записи и агрегирования статистики LLM-инференса.

    Отвечает за:
     - подключение к табличному хранилищу;
     - добавление новых записей о вызовах LLM (add_values);
     - расчёт агрегирующих метрик по заданным колонкам (calculate_stat);
     - очистку таблицы статистики (clear).
    """

    def __init__(self, config: Union[Dict, AgentStatAnalyzerConfig] = AgentStatAnalyzerConfig()):
        if isinstance(config, dict):
            config: AgentStatAnalyzerConfig = AgentStatAnalyzerConfig.from_dict(config)
        else:
            config.formate_fields()
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
        """Вычисляет агрегирующие метрики по колонкам, указанным в конфигурации.

        :return: Словарь, где ключами являются имена колонок, а значениями — словари, в которых ключами являются имена метрик, а значениями — вычисленные агрегированные значения.
        :rtype: Dict[str, Dict[str, Union[float, int]]]
        """
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

    def clear(self) -> None:
        self.db_conn.clear()

    def close_connection(self):
        # print("closing astat-cache conn")
        self.db_conn.close_connection()
