from typing import Dict

from .utils import AbstractTableDatabaseConnection, TableDBConnectionConfig
from .connectors import SQLite3TableConnector, InMemoryTableConnector

from .connectors.configs import DEFAULT_SQLITE3TABLE_CONFIG, DEFAULT_INMEMORYTABLE_CONFIG

DEFAULT_TABLEDB_CONFIGS: Dict[str, TableDBConnectionConfig] = {
    'sqlite3': DEFAULT_SQLITE3TABLE_CONFIG,
    'inmemory_table': DEFAULT_INMEMORYTABLE_CONFIG
}

AVAILABLE_TABLEDB_CONNECTORS: Dict[str, AbstractTableDatabaseConnection] = {
    'sqlite3': SQLite3TableConnector,
    'inmemory_table': InMemoryTableConnector
}
