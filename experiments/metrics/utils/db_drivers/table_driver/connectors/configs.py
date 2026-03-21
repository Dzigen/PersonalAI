from ..utils import TableDBConnectionConfig

DEFAULT_SQLITE3TABLE_CONFIG = TableDBConnectionConfig(
    params={
        'database_path': "./personalai_tmp/volumes/sqlite3"
    }
)

DEFAULT_INMEMORYTABLE_CONFIG = TableDBConnectionConfig(
    params={
        'load_from_disk': False,
        'tablestore_dump_name': None,
        'max_storage': 5e+8,
        'load_dump_dir': "./personalai_tmp/volumes/inmemory_table",
        'save_on_disk': True,
        'save_dump_dir': "./personalai_tmp/volumes/inmemory_table",
        'rewrite': False
    }
)
