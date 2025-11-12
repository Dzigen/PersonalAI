import sys
# TO CHANGE
PROJECT_BASE_DIR = '../'
sys.path.insert(0, PROJECT_BASE_DIR)

from src.utils.data_structs import NodeCreator, Relation, RelationType, NodeType, TripletCreator

# nodes
OBJECT_NODE1 = NodeCreator.create(
    name='abc', n_type=NodeType.object, prop={'k1': 'v1'})
OBJECT_NODE2 = NodeCreator.create(
    name='def', n_type=NodeType.object, prop={'k2': 'v2'})
OBJECT_NODE3 = NodeCreator.create(
    name='ghi', n_type=NodeType.object, prop={'k3': 'v3'})
OBJECT_NODE4 = NodeCreator.create(
    name='yhn', n_type=NodeType.object, prop={'k13': 'v13'})

THESIS_NODE1 = NodeCreator.create(
    name='qwerty', n_type=NodeType.hyper, prop={'k4': 'v4'})
THESIS_NODE2 = NodeCreator.create(
    name='asdfgh', n_type=NodeType.hyper, prop={'k5': 'v5'})
THESIS_NODE3 = NodeCreator.create(
    name='zxcvbn', n_type=NodeType.hyper, prop={'k6': 'v6'})
THESIS_NODE1_1 = NodeCreator.create(
    name='abc', n_type=NodeType.hyper, prop={'k1': 'v1'})

EPISODIC_NODE1 = NodeCreator.create(
    name='uiop', n_type=NodeType.episodic, prop={'k7': 'v7'})
EPISODIC_NODE2 = NodeCreator.create(
    name='jkl', n_type=NodeType.episodic, prop={'k8': 'v8'})
EPISODIC_NODE3 = NodeCreator.create(
    name='mnbv', n_type=NodeType.episodic, prop={'k9': 'v9'})
EPISODIC_NODE3_1 = NodeCreator.create(
    name='ghi', n_type=NodeType.episodic, prop={'k3': 'v3'})
EPISODIC_NODE3_2 = NodeCreator.create(
    name='zxcvbn', n_type=NodeType.episodic, prop={'k6': 'v6'})

# triplets
SIMPLE_TRIPLET1 = TripletCreator.create(start_node=OBJECT_NODE1, relation=Relation(
    name='simple1', type=RelationType.simple, prop={'k10': 'v10'}), end_node=OBJECT_NODE2)
SIMPLE_TRIPLET1_2 = TripletCreator.create(start_node=OBJECT_NODE1, relation=Relation(
    name='simple1_1', type=RelationType.simple, prop={'k16': 'v16'}), end_node=OBJECT_NODE2)

SIMPLE_TRIPLET2 = TripletCreator.create(start_node=OBJECT_NODE2, relation=Relation(
    name='simple2', type=RelationType.simple, prop={'k11': 'v11'}), end_node=OBJECT_NODE3)
SIMPLE_TRIPLET3 = TripletCreator.create(start_node=OBJECT_NODE3, relation=Relation(
    name='simple3', type=RelationType.simple, prop={'k12': 'v12'}), end_node=OBJECT_NODE1)
SIMPLE_TRIPLET4 = TripletCreator.create(start_node=OBJECT_NODE3, relation=Relation(
    name='simple4', type=RelationType.simple, prop={'k14': 'v14'}), end_node=OBJECT_NODE4)
SIMPLE_TRIPLET5 = TripletCreator.create(start_node=OBJECT_NODE1, relation=Relation(
    name='simple5', type=RelationType.simple, prop={'k15': 'v15'}), end_node=OBJECT_NODE1)


THESIS_TRIPLET1 = TripletCreator.create(start_node=OBJECT_NODE1, relation=Relation(
    name='hyper', type=RelationType.hyper), end_node=THESIS_NODE1)
THESIS_TRIPLET2 = TripletCreator.create(start_node=OBJECT_NODE2, relation=Relation(
    name='hyper', type=RelationType.hyper), end_node=THESIS_NODE1)
THESIS_TRIPLET3 = TripletCreator.create(start_node=OBJECT_NODE3, relation=Relation(
    name='hyper', type=RelationType.hyper), end_node=THESIS_NODE2)


EPISODIC_TRIPLET1 = TripletCreator.create(start_node=OBJECT_NODE1, relation=Relation(
    name='episodic', type=RelationType.episodic), end_node=EPISODIC_NODE1)
EPISODIC_TRIPLET2 = TripletCreator.create(start_node=OBJECT_NODE2, relation=Relation(
    name='episodic', type=RelationType.episodic), end_node=EPISODIC_NODE1)
EPISODIC_TRIPLET3 = TripletCreator.create(start_node=OBJECT_NODE3, relation=Relation(
    name='episodic', type=RelationType.episodic), end_node=EPISODIC_NODE2)
EPISODIC_TRIPLET4 = TripletCreator.create(start_node=THESIS_NODE2, relation=Relation(
    name='episodic', type=RelationType.episodic), end_node=EPISODIC_NODE2)


# 8.1 (object[same_str])->(episodic) ; (hyper[same_str])->(episodic)
EPISODIC_TRIPLET5 = TripletCreator.create(start_node=OBJECT_NODE1, relation=Relation(
    name='episodic', type=RelationType.episodic), end_node=EPISODIC_NODE2)
EPISODIC_TRIPLET6 = TripletCreator.create(start_node=THESIS_NODE1_1, relation=Relation(
    name='episodic', type=RelationType.episodic), end_node=EPISODIC_NODE2)

# 8.2 (hyper)->(episodic) | THESIS_NODE3 THESIS_NODE3_2
EPISODIC_TRIPLET7 = TripletCreator.create(start_node=THESIS_NODE3, relation=Relation(
    name='episodic', type=RelationType.episodic), end_node=EPISODIC_NODE3_2 )

# 8.3 (object)->(episodic) | EPISODIC_NODE3_1 OBJECT_NODE3
EPISODIC_TRIPLET8 = TripletCreator.create(start_node=OBJECT_NODE3, relation=Relation(
    name='episodic', type=RelationType.episodic), end_node=EPISODIC_NODE3_1 )

# 8.4 (object)->(hyper) | OBJECT_NODE1 THESIS_NODE1_1
THESIS_TRIPLET4 = TripletCreator.create(start_node=OBJECT_NODE1, relation=Relation(
    name='hyper', type=RelationType.hyper), end_node=THESIS_NODE1_1)
