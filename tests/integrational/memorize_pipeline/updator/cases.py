import pytest

import sys
# TO CHANGE
PROJECT_BASE_DIR = '../'
sys.path.insert(0, PROJECT_BASE_DIR)

from src.utils import TripletCreator, NodeCreator, RelationCreator, NodeType, RelationType

OBJECT_NODE1 = NodeCreator.create(n_type=NodeType.object, name='qw')
OBJECT_NODE2 = NodeCreator.create(n_type=NodeType.object, name='er')
OBJECT_NODE3 = NodeCreator.create(n_type=NodeType.object, name='ty')
OBJECT_NODE4 = NodeCreator.create(n_type=NodeType.object, name='ui')
OBJECT_NODE5 = NodeCreator.create(n_type=NodeType.object, name='op')
OBJECT_NODE6 = NodeCreator.create(n_type=NodeType.object, name='as')
OBJECT_NODE7 = NodeCreator.create(n_type=NodeType.object, name='df')
OBJECT_NODE8 = NodeCreator.create(n_type=NodeType.object, name='gh')

SIMPLE_REL1 = RelationCreator.create(r_type=RelationType.simple, name='qaz')
SIMPLE_REL2 = RelationCreator.create(r_type=RelationType.simple, name='wsx')
SIMPLE_REL3 = RelationCreator.create(r_type=RelationType.simple, name='edc')

SIMPLE_TRIPLET1 = TripletCreator.create(
    start_node=OBJECT_NODE1,relation=SIMPLE_REL1,end_node=OBJECT_NODE2)
SIMPLE_TRIPLET2 = TripletCreator.create(
    start_node=OBJECT_NODE6,relation=SIMPLE_REL2,end_node=OBJECT_NODE7)
SIMPLE_TRIPLET3 = TripletCreator.create(
    start_node=OBJECT_NODE6,relation=SIMPLE_REL3,end_node=OBJECT_NODE8)

HYPER_NODE1 = NodeCreator.create(n_type=NodeType.hyper, name="qqq www eee")
HYPER_NODE2 = NodeCreator.create(n_type=NodeType.hyper, name="aaa sss ddd")

HYPER_REL = RelationCreator.create(r_type=RelationType.hyper, name='hyper')

HYPER_TRIPLET1 = TripletCreator.create(
    start_node=OBJECT_NODE2, relation=HYPER_REL, end_node=HYPER_NODE1)
HYPER_TRIPLET2 = TripletCreator.create(
    start_node=OBJECT_NODE3, relation=HYPER_REL, end_node=HYPER_NODE1)
HYPER_TRIPLET3 = TripletCreator.create(
    start_node=OBJECT_NODE4, relation=HYPER_REL, end_node=HYPER_NODE1)
HYPER_TRIPLET4 = TripletCreator.create(
    start_node=OBJECT_NODE5, relation=HYPER_REL, end_node=HYPER_NODE2)
HYPER_TRIPLET5 = TripletCreator.create(
    start_node=OBJECT_NODE6, relation=HYPER_REL, end_node=HYPER_NODE2)

# -------- SIMPLE GRAPH --------
INIT_SIMPLE_KNOWLEDGE_GRAPH = [
    SIMPLE_TRIPLET1, SIMPLE_TRIPLET2, SIMPLE_TRIPLET3,
    HYPER_TRIPLET1, HYPER_TRIPLET2, HYPER_TRIPLET3,
    HYPER_TRIPLET4, HYPER_TRIPLET5
]

# SIMPLE_TRIPLETS
TRIPLET_EMPTY_ANSWER = '[]'

# 1. нуль сопоставленных вершин
TEST_SIMPLE_TRIPLET1 = ...

# 2. нуль смежных вершин
TEST_SIMPLE_TRIPLET2 = ...

# 3. нуль ids от agent-солвера
TEST_SIMPLE_TRIPLET3 = ...

# 4. найден один устаревший триплет
TEST_SIMPLE_TRIPLET4 = ...
TRIPLET_ANSWER1 = ...

# 5. найдено несколько устаревших триплетов (разные замены)
TEST_SIMPLE_TRIPLET5 = ...
TRIPLET_ANSWER2 = ...

# 6. найдено несколько устаревших триплетов (итеративная замена того же ребра)
TEST_SIMPLE_TRIPLET6 = ...
TRIPLET_ANSWER3 = ...

# 7. ошибка при разборе сгенерированного ответа (parser error)
BAD_SIMPLE_ANSWER = ...

# -------- HYPER GRAPH --------

INIT_HYPER_KNOWLEDGE_GRAPH = [
    ...
]

# -------- EPISODIC GRAPH --------

INIT_EPISODIC_KNOWLEDGE_GRAPH = [
    ...
]
