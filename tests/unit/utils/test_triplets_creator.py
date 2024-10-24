import pytest
import hashlib

import sys
sys.path.insert(0, "../../")
from src.utils.data_structs import TripletCreator, Node, Relation, NodeType, RelationType

@pytest.mark.parametrize("params, expected", [
    ({'start_n': Node(name='a', type=NodeType.object), 'rel': Relation(name='b', type=RelationType.simple, prop={"time": '1'}), 'end_n': Node(name='c', type=NodeType.object)}, {'str_triplet': "1: a b c"}),
    ({'start_n': Node(name='a', type=NodeType.object, prop={'1': '2'}), 'rel': Relation(name='b', type=RelationType.simple, prop={'3': '4'}), 'end_n': Node(name='c', type=NodeType.object, prop={'5': '6'})}, {'str_triplet': "a (1: 2) b (3: 4) c (5: 6)"}),
    ({'start_n': Node(name='a', type=NodeType.object, prop={'1': '2'}), 'rel': Relation(name='b', type=RelationType.hyper), 'end_n': Node(name='c', type=NodeType.hyper, prop={'5': '6', 'time': "t"})}, {'str_triplet': "t: c (5: 6)"}),
    ({'start_n': Node(name='a', type=NodeType.object, prop={'1': '2'}), 'rel': Relation(name='b', type=RelationType.hyper), 'end_n': Node(name='c', type=NodeType.episodic, prop={'5': '6', 'time': "t"})}, {'str_triplet': "t: c (5: 6)"}),
])
def test_craete_triplet(params, expected):
    triplet = TripletCreator.create(
        start_node=params['start_n'],
        relation=params['rel'],
        end_node=params['end_n'])

    expected_id = hashlib.md5(expected['str_triplet'].encode()).hexdigest()
    assert triplet.id == expected_id
    assert triplet.stringified == expected['str_triplet']
    assert triplet.start_node.id is None
    assert triplet.relation.id is None
    assert triplet.end_node.id is None
