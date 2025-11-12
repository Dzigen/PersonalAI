import numpy as np

import sys
sys.path.insert(0, "../")

from src.pipelines.qa.kg_reasoning.weak_reasoner.knowledge_retriever.traversal_methods.BeamSearchTripletsRetriever import TraversingPath
from src.utils.data_structs import NodeInfo, NodeType

# raw_score, expected_value, exception
CALCULATE_TRIPLET_SCORE_TEST_CASES = [
    # 1. невалидный тип входного значения
    # 1.1 int
    (1, None, True),
    # 1.2 str
    ("0.5", None, True),
    # 1.3 None
    (None, None, True),
    # 2. значение не в заданном диапазоне
    (-0.5, None, True),
    (1.5, None, True),
    # 3. получение максимально-возможного значения
    (1.0, 10e+5, False),
    # 4. стандартное поведение
    # 4.1 большое cos-расстояние = мальнькая cos-близость
    (0.9, -np.log(0.1), False),
    # 4.2 маленькое cos-расстояние = большая cos-близость
    (0.1, -np.log(0.9), False),
    # 4.3 небольшое cos-расстояние = небольшая cos-близость
    (0.5, -np.log(0.5), False)
]

EMPTY_TPATH = TraversingPath(
    path=[], unique_ntypedids=set(),
    unique_tids=set(), accum_score=0.0)

OBJECT_NODEINFO1 = NodeInfo(id='n_id1', type=NodeType.object)
OBJECT_NODEINFO2 = NodeInfo(id='n_id2', type=NodeType.object)
OBJECT_NODEINFO3 = NodeInfo(id='n_id3', type=NodeType.object)
OBJECT_NODEINFO4 = NodeInfo(id='n_id4', type=NodeType.object)

SIMPLE_TPATH1 = TraversingPath(
    path=[(OBJECT_NODEINFO1, 't_id1', OBJECT_NODEINFO2)],
    unique_ntypedids={OBJECT_NODEINFO1.to_str(), OBJECT_NODEINFO2.to_str()},
    unique_tids={'t_id1'},
    accum_score=0.2)

SIMPLE_TPATH2 = TraversingPath(
    path=[(OBJECT_NODEINFO1, 't_id1', OBJECT_NODEINFO2),
          (OBJECT_NODEINFO2, 't_id2', OBJECT_NODEINFO3)],
    unique_ntypedids={OBJECT_NODEINFO1.to_str(), OBJECT_NODEINFO2.to_str(), OBJECT_NODEINFO3.to_str()},
    unique_tids={'t_id1', 't_id2'},
    accum_score=0.3)

SIMPLE_TPATH3 = TraversingPath(
    path=[(OBJECT_NODEINFO1, 't_id1', OBJECT_NODEINFO2),
          (OBJECT_NODEINFO2, 't_id3', OBJECT_NODEINFO4)],
    unique_ntypedids={OBJECT_NODEINFO1.to_str(), OBJECT_NODEINFO2.to_str(), OBJECT_NODEINFO4.to_str()},
    unique_tids={'t_id1', 't_id3'},
    accum_score=0.4)

SIMPLE_TPATH3_N1 = TraversingPath(
    path=[(OBJECT_NODEINFO1, 't_id1', OBJECT_NODEINFO2),
          (OBJECT_NODEINFO2, 't_id3', OBJECT_NODEINFO4),
          (OBJECT_NODEINFO4, 't_id4', OBJECT_NODEINFO2)],
    unique_ntypedids={OBJECT_NODEINFO1.to_str(), OBJECT_NODEINFO2.to_str(), OBJECT_NODEINFO4.to_str()},
    unique_tids={'t_id1', 't_id3', 't_id4'},
    accum_score=0.7)

# pinfo, triplet_scores, expected_new_tpaths, exception
EXTEND_TPATH_TEST_CASES = [
    # пустой базовый путь
    (EMPTY_TPATH, [("t_id1", OBJECT_NODEINFO1, 0.2)], None, True),
    # несколько разных вершин для добавления в путь
    (SIMPLE_TPATH1, [
        ("t_id2", OBJECT_NODEINFO3, 0.1),
        ("t_id3", OBJECT_NODEINFO4, 0.2)], [SIMPLE_TPATH2, SIMPLE_TPATH3], False),
    # добавляемая вершина уже есть в пути
    (SIMPLE_TPATH3, [("t_id4", OBJECT_NODEINFO2, 0.3)], [SIMPLE_TPATH3_N1], False),
    # добавляемый триплет уже есть в пути
    (SIMPLE_TPATH3_N1, [("t_id3", OBJECT_NODEINFO4, 0.3)], None, True),
    # нуль новых триплетов для добавления в путь
    (SIMPLE_TPATH3, [], [], False)
]
