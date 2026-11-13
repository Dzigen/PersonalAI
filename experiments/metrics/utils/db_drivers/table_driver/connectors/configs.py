from ..utils import TableDBConnectionConfig

DEFAULT_SQLITE3TABLE_CONFIG = TableDBConnectionConfig(
)

DEFAULT_INMEMORYTABLE_CONFIG = TableDBConnectionConfig(
    params={
        'max_storage': 5e+8,
        'save_on_disk': True,
        'rewrite': False
    }
)
