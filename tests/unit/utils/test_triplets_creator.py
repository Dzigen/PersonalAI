import pytest
import hashlib

import sys
sys.path.insert(0, "../../")
from src.utils.data_structs import TripletCreator, NodeCreator, Node, Relation, NodeType, RelationType, create_id

STRING_PROP_VALUE = 'string_value'
INT_PROP_VALUE = 1001
TEST_TIME = '12.12.2012'
TEST_NODE_NAME = 'abc'
TEST_REL_NAME = 'def'
TEST_ID = 'id123'

TEST_PROPS_WITH_TIME = {'time': TEST_TIME}
TEST_PROPS_WO_TIME = {'p1': STRING_PROP_VALUE, 'p2': INT_PROP_VALUE}
TEST_PROPS_WITH_SPECIAL = {
    'name': STRING_PROP_VALUE, 'type': STRING_PROP_VALUE, 'raw_time': STRING_PROP_VALUE,
    'time': TEST_TIME, 'str_id': STRING_PROP_VALUE}

###################

TEST_OBJECT_NODE = NodeCreator.create(name=TEST_NODE_NAME, type=NodeType.object)

TEST_EXPECTED_SIMPLE_TRIPLET_STR1 = f'{TEST_NODE_NAME} {TEST_REL_NAME} {TEST_NODE_NAME}'
TEST_EXPECTED_SIMPLE_TRIPLET_WITH_TIME_STR2 = f'{TEST_TIME}: {TEST_EXPECTED_SIMPLE_TRIPLET_STR1}'
TEST_EXPECTED_SIMPLE_TRIPLET_STR3 = f'{TEST_NODE_NAME} {TEST_REL_NAME} (p1: {STRING_PROP_VALUE}; p2: {INT_PROP_VALUE}) {TEST_NODE_NAME}'
TEST_EXPECTED_SIMPLE_TRIPLET_STR4 = f'{TEST_NODE_NAME}  {TEST_NODE_NAME}'

@pytest.mark.parametrize("params, expected", [
    # сохранить строковое представление в триплете
    ({'sn': TEST_OBJECT_NODE, 'en': TEST_OBJECT_NODE, 'r_name': TEST_REL_NAME, 'r_prop': dict(), 'id': None, 's_str': True}, {'str': TEST_EXPECTED_SIMPLE_TRIPLET_STR1}),
    # не сохранять строковое представление в триплете
    ({'sn': TEST_OBJECT_NODE, 'en': TEST_OBJECT_NODE, 'r_name': TEST_REL_NAME, 'r_prop': dict(), 'id': None, 's_str': False}, {'str': None}),
    # назначить собственный идентификатор триплету
    ({'sn': TEST_OBJECT_NODE, 'en': TEST_OBJECT_NODE, 'r_name': TEST_REL_NAME, 'r_prop': dict(), 'id': TEST_ID, 's_str': False}, {'str': None}),
    # строковое представление с отметкой времени
    ({'sn': TEST_OBJECT_NODE, 'en': TEST_OBJECT_NODE, 'r_name': TEST_REL_NAME, 'r_prop': TEST_PROPS_WITH_TIME, 'id': None, 's_str': True}, {'str': TEST_EXPECTED_SIMPLE_TRIPLET_WITH_TIME_STR2}),
    # строкое представление со свойствами
    ({'sn': TEST_OBJECT_NODE, 'en': TEST_OBJECT_NODE, 'r_name': TEST_REL_NAME, 'r_prop': TEST_PROPS_WO_TIME, 'id': None, 's_str': True}, {'str': TEST_EXPECTED_SIMPLE_TRIPLET_STR3}),
    # строкоове представление без свойств/имён
    ({'sn': TEST_OBJECT_NODE, 'en': TEST_OBJECT_NODE, 'r_name': '', 'r_prop': dict(), 'id': None, 's_str': True}, {'str': TEST_EXPECTED_SIMPLE_TRIPLET_STR4}),
    # строковое представление со специальными свойствами
    ({'sn': TEST_OBJECT_NODE, 'en': TEST_OBJECT_NODE, 'r_name': TEST_REL_NAME, 'r_prop': TEST_PROPS_WITH_SPECIAL, 'id': None, 's_str': True}, {'str': TEST_EXPECTED_SIMPLE_TRIPLET_WITH_TIME_STR2}),
])
def test_create_simple_triplet(params, expected):
    rel = Relation(name=params['r_name'], prop=params['r_prop'], type=RelationType.simple)
    triplet = TripletCreator.create(
        start_node=params['sn'], relation=rel,
        end_node=params['en'], add_stringified_triplet=params['s_str'],
        t_id=params['id'])

    if params['id'] is not None:
        assert triplet.id == params['id']
    else:
        assert triplet.id == create_id(''.join([triplet.start_node.id, triplet.relation.id, triplet.end_node.id]))

    assert triplet.relation.id == create_id(TripletCreator.stringify(triplet)[1])

    if params['s_str']:
        assert expected['str'] == triplet.stringified
    else:
        assert triplet.stringified is None

###################

TEST_THESIS_NODE1 = NodeCreator.create(name=TEST_NODE_NAME, type=NodeType.hyper)
TEST_THESIS_NODE2 = NodeCreator.create(name=TEST_NODE_NAME, type=NodeType.hyper, prop=TEST_PROPS_WITH_TIME)
TEST_THESIS_NODE3 = NodeCreator.create(name=TEST_NODE_NAME, type=NodeType.hyper, prop=TEST_PROPS_WO_TIME)
TEST_THESIS_NODE4 = NodeCreator.create(name=TEST_NODE_NAME, type=NodeType.hyper, prop=TEST_PROPS_WITH_SPECIAL)

TEST_EXPECTED_HYPER_TRIPLET_STR1 = f"{TEST_NODE_NAME}"
TEST_EXPECTED_HYPER_TRIPLET_STR2 = f"{TEST_TIME}: {TEST_NODE_NAME}"
TEST_EXPECTED_HYPER_TRIPLET_STR3 = f"{TEST_EXPECTED_HYPER_TRIPLET_STR1} (p1: {STRING_PROP_VALUE}; p2: {INT_PROP_VALUE})"

@pytest.mark.parametrize("params, expected", [
    # сохранить строковое представление в триплете
    ({'sn': TEST_OBJECT_NODE, 'en': TEST_THESIS_NODE1, 'r_name': TEST_REL_NAME, 'r_prop': dict(), 'id': None, 's_str': True}, {'str': TEST_EXPECTED_HYPER_TRIPLET_STR1}),
    # не сохранять строковое представление в триплете
    ({'sn': TEST_OBJECT_NODE, 'en': TEST_THESIS_NODE1, 'r_name': TEST_REL_NAME, 'r_prop': dict(), 'id': None, 's_str': False}, {'str': None}),
    # назначить собственный идентификатор триплету
    ({'sn': TEST_OBJECT_NODE, 'en': TEST_THESIS_NODE1, 'r_name': TEST_REL_NAME, 'r_prop': dict(), 'id': TEST_ID, 's_str': False}, {'str': None}),
    # строковое представление с отметкой времени
    ({'sn': TEST_OBJECT_NODE, 'en': TEST_THESIS_NODE2, 'r_name': TEST_REL_NAME, 'r_prop': TEST_PROPS_WO_TIME, 'id': None, 's_str': True}, {'str': TEST_EXPECTED_HYPER_TRIPLET_STR2}),
    # строкое представление со свойствами
    ({'sn': TEST_OBJECT_NODE, 'en': TEST_THESIS_NODE3, 'r_name': TEST_REL_NAME, 'r_prop': TEST_PROPS_WO_TIME, 'id': None, 's_str': True}, {'str': TEST_EXPECTED_HYPER_TRIPLET_STR3}),
    # строкоове представление без свойств/имён
    ({'sn': TEST_OBJECT_NODE, 'en': TEST_THESIS_NODE1, 'r_name': '', 'r_prop': dict(), 'id': None, 's_str': True}, {'str': TEST_EXPECTED_HYPER_TRIPLET_STR1}),
    # строковое представление со специальными свойствами
    ({'sn': TEST_OBJECT_NODE, 'en': TEST_THESIS_NODE4, 'r_name': TEST_REL_NAME, 'r_prop': TEST_PROPS_WITH_SPECIAL, 'id': None, 's_str': True}, {'str': TEST_EXPECTED_HYPER_TRIPLET_STR2}),
])
def test_create_hyper_triplet(params, expected):
    rel = Relation(name=params['r_name'], prop=params['r_prop'], type=RelationType.hyper)
    triplet = TripletCreator.create(
        start_node=params['sn'], relation=rel,
        end_node=params['en'], add_stringified_triplet=params['s_str'],
        t_id=params['id'])

    if params['id'] is not None:
        assert triplet.id == params['id']
    else:
        assert triplet.id == create_id(''.join([triplet.start_node.id, triplet.relation.id, triplet.end_node.id]))

    assert triplet.relation.id == create_id(TripletCreator.stringify(triplet)[1])

    if params['s_str']:
        assert expected['str'] == triplet.stringified
    else:
        assert triplet.stringified is None

###################

TEST_EPISODIC_NODE1 = NodeCreator.create(name=TEST_NODE_NAME, type=NodeType.episodic)
TEST_EPISODIC_NODE2 = NodeCreator.create(name=TEST_NODE_NAME, type=NodeType.episodic, prop=TEST_PROPS_WITH_TIME)
TEST_EPISODIC_NODE3 = NodeCreator.create(name=TEST_NODE_NAME, type=NodeType.episodic, prop=TEST_PROPS_WO_TIME)
TEST_EPISODIC_NODE4 = NodeCreator.create(name=TEST_NODE_NAME, type=NodeType.episodic, prop=TEST_PROPS_WITH_SPECIAL)

TEST_EXPECTED_EPISODIC_TRIPLET_STR1 = f"{TEST_NODE_NAME}"
TEST_EXPECTED_EPISODIC_TRIPLET_STR2 = f"{TEST_TIME}: {TEST_NODE_NAME}"
TEST_EXPECTED_EPISODIC_TRIPLET_STR3 = f"{TEST_EXPECTED_EPISODIC_TRIPLET_STR1} (p1: {STRING_PROP_VALUE}; p2: {INT_PROP_VALUE})"

@pytest.mark.parametrize("params, expected", [
    # сохранить строковое представление в триплете
    ({'sn': TEST_OBJECT_NODE, 'en': TEST_EPISODIC_NODE1, 'r_name': TEST_REL_NAME, 'r_prop': dict(), 'id': None, 's_str': True}, {'str': TEST_EXPECTED_EPISODIC_TRIPLET_STR1}),
    # не сохранять строковое представление в триплете
    ({'sn': TEST_OBJECT_NODE, 'en': TEST_EPISODIC_NODE1, 'r_name': TEST_REL_NAME, 'r_prop': dict(), 'id': None, 's_str': False}, {'str': None}),
    # назначить собственный идентификатор триплету
    ({'sn': TEST_OBJECT_NODE, 'en': TEST_EPISODIC_NODE1, 'r_name': TEST_REL_NAME, 'r_prop': dict(), 'id': TEST_ID, 's_str': False}, {'str': None}),
    # строковое представление с отметкой времени
    ({'sn': TEST_OBJECT_NODE, 'en': TEST_EPISODIC_NODE2, 'r_name': TEST_REL_NAME, 'r_prop': TEST_PROPS_WO_TIME, 'id': None, 's_str': True}, {'str': TEST_EXPECTED_EPISODIC_TRIPLET_STR2}),
    # строкое представление со свойствами
    ({'sn': TEST_OBJECT_NODE, 'en': TEST_EPISODIC_NODE3, 'r_name': TEST_REL_NAME, 'r_prop': TEST_PROPS_WO_TIME, 'id': None, 's_str': True}, {'str': TEST_EXPECTED_EPISODIC_TRIPLET_STR3}),
    # строкоове представление без свойств/имён
    ({'sn': TEST_OBJECT_NODE, 'en': TEST_EPISODIC_NODE1, 'r_name': '', 'r_prop': dict(), 'id': None, 's_str': True}, {'str': TEST_EXPECTED_EPISODIC_TRIPLET_STR1}),
    # строковое представление со специальными свойствами
    ({'sn': TEST_OBJECT_NODE, 'en': TEST_EPISODIC_NODE4, 'r_name': TEST_REL_NAME, 'r_prop': TEST_PROPS_WITH_SPECIAL, 'id': None, 's_str': True}, {'str': TEST_EXPECTED_EPISODIC_TRIPLET_STR2}),
])
def test_create_episodic_triplet(params, expected):
    rel = Relation(name=params['r_name'], prop=params['r_prop'], type=RelationType.episodic)
    triplet = TripletCreator.create(
        start_node=params['sn'], relation=rel,
        end_node=params['en'], add_stringified_triplet=params['s_str'],
        t_id=params['id'])

    if params['id'] is not None:
        assert triplet.id == params['id']
    else:
        assert triplet.id == create_id(''.join([triplet.start_node.id, triplet.relation.id, triplet.end_node.id]))

    assert triplet.relation.id == create_id(TripletCreator.stringify(triplet)[1])

    if params['s_str']:
        assert expected['str'] == triplet.stringified
    else:
        assert triplet.stringified is None

@pytest.mark.parametrize("json_triplet, formated_triplet", [
    # 1. в subject
    # 1.1. не заполнено prop-поле
    # 1.2. не заполнено name-поле
    # 1.2.1 type = 'object'
    # 1.2.2 type = 'hyper'
    # 1.2.3 type = 'episodic'
    # 1.3. не заполнено type-поле
    # 1.4. указано невалидное значение в type-поле
    # 2. В relation
    # 2.1. пустое prop-поле
    # 2.2. не заполнено name-поле
    # 2.2.1 type = 'object'
    # 2.2.2 type = 'hyper'
    # 2.2.3 type = 'episodic'
    # 2.3. не заполнено type-поле
    # 2.4. указано невалидное значение в type-поле
    # 3. В object
    # 3.1. пустое prop-поле
    # 3.2. не заполнено name-поле
    # 3.2.1 type = 'object'
    # 3.2.2 type = 'hyper'
    # 3.2.3 type = 'episodic'
    # 3.3. не заполнено type-поле
    # 3.4. указано невалидное значение в type-поле
])
def test_create_from_json(json_triplet, formated_triplet):
    real_f_triplet = TripletCreator.from_json()
