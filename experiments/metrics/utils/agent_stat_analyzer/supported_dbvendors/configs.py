from .InMemoryStatOperations import InMemoryStatOperations
from .SQLite3StatOperations import SQLite3StatOperations


SUPPORTED_VENDORS = {
    'inmemory_table': InMemoryStatOperations,
    'sqlite3': SQLite3StatOperations
}
