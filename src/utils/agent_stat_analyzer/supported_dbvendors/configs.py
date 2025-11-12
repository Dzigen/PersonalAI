from .InMemoryStatOperations import InMemoryStatOperations
from .MongoStatOperations import MongoStatOperations
from .PostgreSQLStatOperations import PostgreSQLStatOperations
from .MySQLStatOperations import MySQLStatOperations
from .SQLite3StatOperations import SQLite3StatOperations


SUPPORTED_VENDORS = {
    'inmemory_table': InMemoryStatOperations,
    'mongo': MongoStatOperations,
    'postgresql': PostgreSQLStatOperations,
    'mysql': MySQLStatOperations,
    'sqlite3': SQLite3StatOperations
}
