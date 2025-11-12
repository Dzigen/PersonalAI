from typing import Dict

from .utils import AbstractTableDatabaseConnection, TableDBConnectionConfig
from .connectors import MongoTableConnector, MySQLTableConnector, PostgreSQLTableConnector, SQLite3TableConnector, InMemoryTableConnector

from .connectors.configs import DEFAULT_MONGOTABLE_CONFIG, DEFAULT_MYSQLTABLE_CONFIG, \
    DEFAULT_POSTGRESQLTABLE_CONFIG, DEFAULT_SQLITE3TABLE_CONFIG, DEFAULT_INMEMORYTABLE_CONFIG

DEFAULT_TABLEDB_CONFIGS: Dict[str, TableDBConnectionConfig] = {
    'mongo': DEFAULT_MONGOTABLE_CONFIG,
    'mysql': DEFAULT_MYSQLTABLE_CONFIG,
    'postgresql': DEFAULT_POSTGRESQLTABLE_CONFIG,
    'sqlite3': DEFAULT_SQLITE3TABLE_CONFIG,
    'inmemory_table': DEFAULT_INMEMORYTABLE_CONFIG
}

AVAILABLE_TABLEDB_CONNECTORS: Dict[str, AbstractTableDatabaseConnection] = {
    'mongo': MongoTableConnector,
    'mysql': MySQLTableConnector,
    'postgresql': PostgreSQLTableConnector,
    'sqlite3': SQLite3TableConnector,
    'inmemory_table': InMemoryTableConnector
}
