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

HYPER_REL = RelationCreator.create(r_type=RelationType.hyper)

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

INIT_KNOWLEDGE_GRAPH = [
    SIMPLE_TRIPLET1, SIMPLE_TRIPLET2, SIMPLE_TRIPLET3,
    HYPER_TRIPLET1, HYPER_TRIPLET2, HYPER_TRIPLET3,
    HYPER_TRIPLET4, HYPER_TRIPLET5
]

# -------- SIMPLE GRAPH --------

# SIMPLE_TRIPLETS
TRIPLET_EMPTY_ANSWER = '[]'

# 1. нуль сопоставленных вершин
TEST_SIMPLE_TRIPLET1 = TripletCreator.create(
    start_node=NodeCreator.create(n_type=NodeType.object, name='qsc'),
    relation=RelationCreator.create(r_type=RelationType.simple, name='esz'),
    end_node=NodeCreator.create(n_type=NodeType.object, name='vuf')
)

# 2. нуль смежных вершин
TEST_SIMPLE_TRIPLET2 = TripletCreator.create(
    start_node=OBJECT_NODE5,
    relation=RelationCreator.create(r_type=RelationType.simple, name='pkn'),
    end_node=NodeCreator.create(n_type=NodeType.object, name='vbn')
)

# 4. найден один устаревший триплет
TEST_SIMPLE_TRIPLET4 = TripletCreator.create(
    start_node=OBJECT_NODE1,
    relation=RelationCreator.create(r_type=RelationType.simple, name='pkn'),
    end_node=OBJECT_NODE2
)
TRIPLET_ANSWER1 = f'[["{SIMPLE_TRIPLET1.start_node.name}, {SIMPLE_TRIPLET1.relation.name}, {SIMPLE_TRIPLET1.end_node.name}" -> "{TEST_SIMPLE_TRIPLET4.start_node.name}, {TEST_SIMPLE_TRIPLET4.relation.name}, {TEST_SIMPLE_TRIPLET4.end_node.name}"]]'

# 5. найдено несколько устаревших триплетов (разные замены)
TEST_SIMPLE_TRIPLET5 = TripletCreator.create(
    start_node=OBJECT_NODE6,
    relation=RelationCreator.create(r_type=RelationType.simple, name='qfj'),
    end_node=OBJECT_NODE8
)
TRIPLET_ANSWER2 = f'[["{SIMPLE_TRIPLET3.start_node.name}, {SIMPLE_TRIPLET3.relation.name}, {SIMPLE_TRIPLET3.end_node.name}" -> "{TEST_SIMPLE_TRIPLET5.start_node.name}, {TEST_SIMPLE_TRIPLET5.relation.name}, {TEST_SIMPLE_TRIPLET5.end_node.name}"]]'

# 6. найдено несколько устаревших триплетов (итеративная замена того же ребра)
TEST_SIMPLE_TRIPLET6 = TripletCreator.create(
    start_node=OBJECT_NODE1,
    relation=RelationCreator.create(r_type=RelationType.simple, name='pkn pppp'),
    end_node=OBJECT_NODE2
)
TRIPLET_ANSWER3 = f'[["{SIMPLE_TRIPLET1.start_node.name}, {SIMPLE_TRIPLET1.relation.name}, {SIMPLE_TRIPLET1.end_node.name}" -> "{TEST_SIMPLE_TRIPLET4.start_node.name}, {TEST_SIMPLE_TRIPLET4.relation.name}, {TEST_SIMPLE_TRIPLET4.end_node.name}"], ["{TEST_SIMPLE_TRIPLET4.start_node.name}, {TEST_SIMPLE_TRIPLET4.relation.name}, {TEST_SIMPLE_TRIPLET4.end_node.name}" -> "{TEST_SIMPLE_TRIPLET6.start_node.name}, {TEST_SIMPLE_TRIPLET6.relation.name}, {TEST_SIMPLE_TRIPLET6.end_node.name}"]]'

# 7. ошибка при разборе сгенерированного ответа (parser error)
BAD_SIMPLE_ANSWER = f'[["{SIMPLE_TRIPLET1.start_node.name} {SIMPLE_TRIPLET1.relation.name} {SIMPLE_TRIPLET1.end_node.name}" -> "{TEST_SIMPLE_TRIPLET4.start_node.name} {TEST_SIMPLE_TRIPLET4.relation.name} {TEST_SIMPLE_TRIPLET4.end_node.name}"]]'

# -------- HYPER GRAPH --------

# 1. нуль сопоставленных вершин
TEST_HYPER_TRIPLET1 = TripletCreator.create(
    start_node=NodeCreator.create(n_type=NodeType.object, name='pppp wwww'),
    relation=RelationCreator.create(r_type=RelationType.hyper),
    end_node=HYPER_NODE1
)

# 2. нуль смежных вершин
TEST_HYPER_TRIPLET2 = TripletCreator.create(
    start_node=OBJECT_NODE7,
    relation=RelationCreator.create(r_type=RelationType.hyper),
    end_node=HYPER_NODE2
)

# 3. найден один устаревший триплет
TEST_HYPER_TRIPLET4 = TripletCreator.create(
    start_node=OBJECT_NODE3,
    relation=RelationCreator.create(r_type=RelationType.hyper),
    end_node=NodeCreator.create(n_type=NodeType.hyper, name='gggg hhhh jjj')
)
HYPER_ANSWER1 = f'["{TEST_HYPER_TRIPLET4.end_node.name} <- {HYPER_NODE1.name}"]'

# 4. найдено несколько устаревших триплетов (разные замены)
TEST_HYPER_TRIPLET5 = TripletCreator.create(
    start_node=OBJECT_NODE4,
    relation=RelationCreator.create(r_type=RelationType.hyper),
    end_node=NodeCreator.create(n_type=NodeType.hyper, name='zzzzz ssss yyy')
)
HYPER_ANSWER2 = f'["{TEST_HYPER_TRIPLET5.end_node.name} <- {HYPER_NODE1.name}"]'

# 5. найдено несколько устаревших триплетов (итеративная замена того же ребра)
TEST_HYPER_TRIPLET6 = TripletCreator.create(
    start_node=TEST_HYPER_TRIPLET4.start_node,
    relation=RelationCreator.create(r_type=RelationType.hyper),
    end_node=NodeCreator.create(n_type=NodeType.hyper, name='sss ddd ooo')
)
HYPER_ANSWER3 = f'["{TEST_HYPER_TRIPLET6.end_node.name} <- {TEST_HYPER_TRIPLET4.end_node.name}"]'

# 6. ошибка при разборе сгенерированного ответа (parser error)
BAD_HYPER_ANSWER = f'[{TEST_HYPER_TRIPLET4.end_node.name} {HYPER_NODE1.name}]'

# -------- EPISODIC GRAPH --------
