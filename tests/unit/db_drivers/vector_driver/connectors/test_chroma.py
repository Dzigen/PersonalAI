import pytest
import numpy as np

import sys
sys.path.insert(0, "../../../../../")

from src.db_drivers.vector_driver import ChromaConnection, VectorDBConnectionConfig, VectorDBInstance

CHROMA_DB_NAME = 'test_name'

@pytest.fixture
def chroma_connection():
    config = VectorDBConnectionConfig(
        path='./tmp/chromadb', db_name=CHROMA_DB_NAME, need_to_clear=True)
    return ChromaConnection(config)

@pytest.mark.parametrize("instances", [
    [VectorDBInstance(id='123', document='a', embedding=np.array([1,2,3])),
     VectorDBInstance(id='1234', document='b', embedding=np.array([4,5,6]))]
])
def test_create(chroma_connection, instances):
    chroma_connection.clear()
    chroma_connection.create(instances)
    unique_ids = set(map(lambda inst: inst.id, instances))
    assert chroma_connection.collection.count() == len(unique_ids)

@pytest.mark.parametrize("instances", [
    [VectorDBInstance(id='123', document='a', embedding=np.array([1,2,3]))]
])
def test_read(chroma_connection, instances):
    chroma_connection.clear()
    chroma_connection.create(instances)

    bad_id = 'qwerty'
    insts_ids = list(map(lambda inst: inst.id, instances))
    insts_ids.append(bad_id)

    output = chroma_connection.read(insts_ids)
    assert len(output) == len(instances)

@pytest.mark.parametrize("instances", [
    [VectorDBInstance(id='123', document='a', embedding=np.array([1,2,3])),
     VectorDBInstance(id='1234', document='a', embedding=np.array([1,2,3]))]
])
def test_delete(chroma_connection, instances):
    chroma_connection.clear()
    chroma_connection.create(instances)
    assert chroma_connection.collection.count() == len(instances)

    insts_ids = list(map(lambda inst: inst.id, instances))
    chroma_connection.delete(insts_ids)
    assert chroma_connection.collection.count() == 0

def test_retrieve(chroma_connection):
    pass
