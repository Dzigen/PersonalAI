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

DEFAULT_SQLITE3TABLE_CONFIG = TableDBConnectionConfig()

DEFAULT_INMEMORYTABLE_CONFIG = TableDBConnectionConfig(
    params={
        'max_storage': 5e+8,
        'save_on_disk': True,
        'rewrite': True
    }
)
