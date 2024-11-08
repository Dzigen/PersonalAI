import pytest

import sys
sys.path.insert(0, "../../")
from src.db_drivers.vector_driver import VectorDriver, VectorDriverConfig, VectorDBConnectionConfig

@pytest.fixture()
def chromadb_conn():
    config = VectorDriverConfig(db_vendor='chroma', db_config=VectorDBConnectionConfig(
            path="./volumes/chroma", db_name='testing', need_to_clear=True))
    return VectorDriver.connect(config)
