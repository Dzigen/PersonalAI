from ..utils import TableDBConnectionConfig

DEFAULT_MONGOTABLE_CONFIG = TableDBConnectionConfig(
    host='localhost', port=27010,
    params={'username': 'user', 'password': 'pass', 'max_storage': -1}
)

DEFAULT_MYSQLTABLE_CONFIG = TableDBConnectionConfig(
    host='localhost', port=3306,
    params={'username': 'personalai', 'password': 'personalai'}
)

DEFAULT_POSTGRESQLTABLE_CONFIG = TableDBConnectionConfig(
    host='localhost', port=5432,
    params={'username': 'personalai', 'password': 'personalai'}
)

DEFAULT_SQLITE3TABLE_CONFIG = TableDBConnectionConfig(
    params={
        'database_dname': f'./personalai/volumes/sqlite3'
    }
)

DEFAULT_INMEMORYTABLE_CONFIG = TableDBConnectionConfig(
    params={
        'tablestore_dump_name': 'inmemory_table_store',
        'load_from_disk': False,
        'max_storage': 5e+8,
        'load_dump_dir': "./personalai/volumes/inmemory_table",
        'save_on_disk': True,
        'save_dump_dir': "./personalai/volumes/inmemory_table"
    }
)
