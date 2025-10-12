from dataclasses import dataclass, field

from .utils import TableDBConnectionConfig, AbstractTableDatabaseConnection
from .configs import DEFAULT_TABLEDB_CONFIGS, AVAILABLE_TABLEDB_CONNECTORS


@dataclass
class TableDriverConfig:
    db_vendor: str = 'sqlite3'
    db_config: TableDBConnectionConfig = field(
        default_factory=lambda: DEFAULT_TABLEDB_CONFIGS['sqlite3'])


class TableDriver:
    @staticmethod
    def connect(config: TableDriverConfig = TableDriverConfig()) -> AbstractTableDatabaseConnection:
        table_conn: AbstractTableDatabaseConnection = AVAILABLE_TABLEDB_CONNECTORS[config.db_vendor](config.db_config)
        table_conn.open_connection()
        return table_conn
