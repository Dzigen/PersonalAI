import pytest

import sys
sys.path.insert(0, "../../")
from src.db_drivers.graph_driver import GraphDriver, GraphDriverConfig, GraphDBConnectionConfig

@pytest.fixture()
def inmemory_conn():
    config = GraphDriverConfig(db_vendor='inmemory', db_config=GraphDBConnectionConfig(
        need_to_clear=True))
    return GraphDriver.connect(config)

@pytest.fixture()
def neo4j_conn():
    config = GraphDriverConfig(db_vendor='neo4j', db_config=GraphDBConnectionConfig(
        db_info={'dbname': 'testing', 'table': 'testing'}
        need_to_clear=True))
    return GraphDriver.connect(config)
