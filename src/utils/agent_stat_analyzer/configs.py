from ...db_drivers.table_driver import TableDBConnectionConfig, TableDriverConfig
from ...db_drivers.table_driver.table_structures import LLMInferenceStat

CREATE_TABLE_SQLQUERY = '''
CREATE TABLE IF NOT EXISTS {table_name} (
    id SERIAL PRIMARY KEY,
    prompt_tokens_amount INT NULL,
    generated_tokens_amount INT NULL,
    preparation_elapsed_time REAL NULL,
    inference_elapsed_time REAL NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
'''

DEFAULT_AGENTSTAT_TABLEDB_DRIVER_CONFIG = TableDriverConfig(
    db_vendor='sqlite3',
    db_config=TableDBConnectionConfig(
        db_info={
            'db': 'default_llmstatdb', 'table': 'default_llmstattable',
            'table_info': LLMInferenceStat,
            'create_table_query': CREATE_TABLE_SQLQUERY
        },
        params={
            'database_path': './personalai_tmp/stat/agent/sqlite3'
        },
        need_to_clear=False
    )
)
