import pytest
import hashlib

import sys
sys.path.insert(0, "../../")
from src.utils.data_structs import TripletCreator, Node, Relation, NodeType, RelationType

STRING_PROP_VALUE = 'string_value'
INT_PROP_VALUE = 1001
TEST_TIME = '12.12.2012'
TEST_NODE_NAME = 'abc'
TEST_REL_NAME = 'def'
TEST_ID = 'id123'

TEST_PROPS_WITH_TIME = {'time': TEST_TIME, 'p1': STRING_PROP_VALUE, 'p2': INT_PROP_VALUE} 
TEST_PROPS_WO_TIME = {'p1': STRING_PROP_VALUE, 'p2': INT_PROP_VALUE} 
TEST_PROPS_WITH_SPECIAL = {
    'name': STRING_PROP_VALUE, 'type': STRING_PROP_VALUE, 'raw_time': STRING_PROP_VALUE, 
    'time': TEST_TIME, 'str_id': STRING_PROP_VALUE}

TEST_OBJECT_NODE = Node(name=TEST_NODE_NAME, type=NodeType.object)
TEST_SIMPLE_REL = Relation(name=TEST_REL_NAME, type=RelationType.simple)

TEST_THESIS_NODE = Node(name=TEST_NODE_NAME, type=NodeType.hyper)
TEST_THESIS_REL = Relation(name=TEST_REL_NAME, rtpe=RelationType.hyper)

TEST_EPISODIC_NODE = Node(name=TEST_NODE_NAME, type=NodeType.episodic)
TEST_EPISODIC_REL = Relation(name=TEST_REL_NAME, rtpe=RelationType.episodic)

@pytest.mark.parametrize("params, expected", [
    # сохранить строковое представление в триплете
    ({'sn': TEST_OBJECT_NODE, 'en': TEST_OBJECT_NODE, 'r': TEST_SIMPLE_REL, 'id': None, 's_str': True}, {'str': ...}),
    # не сохранять строковое представление в триплете
    ({'sn': ..., 'en': ..., 'r': ..., 'id': None, 's_str': False}, {'str': ...}),
    # назначить собственный идентификатор триплету
    ({'sn': ..., 'en': ..., 'r': ..., 'id': TEST_ID, 's_str': True}, {'str': ...}),
    # строковое представление с отметкой времени
    ({'sn': ..., 'en': ..., 'r': ..., 'id': None, 's_str': True}, {'str': ...}),
    # строковое представление без отметки времени
    ({'sn': ..., 'en': ..., 'r': ..., 'id': None, 's_str': True}, {'str': ...}),
    # строкое представление со свойствами
    ({'sn': ..., 'en': ..., 'r': ..., 'id': None, 's_str': True}, {'str': ...}),
    # строкоове представление без свойств/имён
    ({'sn': ..., 'en': ..., 'r': ..., 'id': None, 's_str': True}, {'str': ...}),
    # строковое представление со специальными свойствами
    ({'sn': ..., 'en': ..., 'r': ..., 'id': None, 's_str': True}, {'str': ...}),
])
def test_create_simple_triplet(params, expected):
    triplet = TripletCreator.create(
        start_node=params['sn'], relation=params['r'], 
        end_node=params['en'], add_stringified_triplet=params['s_str'], 
        t_id=params['id'])
    
    if params['id'] is not None:
        assert triplet.id == params['id']

    if params['add_stringified_node']:
        assert expected['str'] == triplet.stringified
    else:
        assert triplet.stringified is None

def test_create_hyper_triplet(params, expected):
    triplet = TripletCreator.create(
        start_node=params['sn'], relation=params['r'], 
        end_node=params['en'], add_stringified_triplet=params['s_str'], 
        t_id=params['id'])
    
    if params['id'] is not None:
        assert triplet.id == params['id']

    if params['add_stringified_node']:
        assert expected['str'] == triplet.stringified
    else:
        assert triplet.stringified is None

def test_create_episodic_triplet(params, expected):
    triplet = TripletCreator.create(
        start_node=params['sn'], relation=params['r'], 
        end_node=params['en'], add_stringified_triplet=params['s_str'], 
        t_id=params['id'])
    
    if params['id'] is not None:
        assert triplet.id == params['id']

    if params['add_stringified_node']:
        assert expected['str'] == triplet.stringified
    else:
        assert triplet.stringified is None