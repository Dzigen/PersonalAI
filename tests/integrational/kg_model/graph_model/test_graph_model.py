import pytest
from typing import List, Dict, Set
import sys
sys.path.insert(0, "../")

from .cases import GM_POPULATED_CREATE_TEST_CASES, GM_POPULATED_DELETE_TEST_CASES
from src.kg_model import GraphModel
from src.utils import Triplet
from src.utils.data_structs import RelationInfo, NodeInfo

@pytest.mark.parametrize("init_triplets, expected_init_count, expected_create_info, graph_model", GM_POPULATED_CREATE_TEST_CASES, indirect=['graph_model'])
def test_create_triplets(init_triplets: List[Triplet], expected_init_count: Dict[str, int],
                         expected_create_info: Dict[str, Set[str]], graph_model: GraphModel):
    graph_model.clear()

    real_create_info = graph_model.create_triplets(init_triplets, batch_size=1)

    print("Triplets")
    for triplet in init_triplets:
        print(triplet)
    print("Real create:")
    print(real_create_info)
    print("Expected create:")
    print(expected_create_info)

    #
    assert real_create_info.keys() == expected_create_info.keys()
    for n_type, real_nids in real_create_info['nodes'].items():
        assert expected_create_info['nodes'].get(n_type, set()) == real_nids
    for r_type, real_tids in real_create_info['triplets'].items():
        assert expected_create_info['triplets'].get(r_type, set()) == real_tids

    #
    real_items_count = graph_model.count_items()
    assert real_items_count.keys() == expected_init_count.keys()
    for expexted_k, expected_val in expected_init_count.items():
        assert real_items_count[expexted_k] == expected_val

    #
    for n_type, n_ids in real_create_info['nodes'].items():
        for n_id in n_ids:
            assert graph_model.db_conn.item_exist(NodeInfo(id=n_id, type=n_type), id_type='node')
    for r_type, t_ids in real_create_info['triplets'].items():
        for t_id in t_ids:
            assert graph_model.db_conn.item_exist(t_id, id_type='triplet')

    #
    for triplet in init_triplets:
        assert graph_model.db_conn.item_exist(triplet.start_node.get_info(), id_type='node')
        assert graph_model.db_conn.item_exist(triplet.end_node.get_info(), id_type='node')
        assert graph_model.db_conn.item_exist(triplet.id, id_type='triplet')
        assert graph_model.db_conn.item_exist(triplet.relation.get_info(), id_type='relation')

    graph_model.clear()


@pytest.mark.parametrize("init_triplets, expected_create_info, expected_init_count, triplets_to_delete, expected_delete_ginfo, expected_final_count, expected_delete_vinfo, graph_model", GM_POPULATED_DELETE_TEST_CASES, indirect=['graph_model'])
def test_delete_triplets(init_triplets: List[Triplet], expected_create_info: Dict[str, Set[str]], expected_init_count: Dict[str, int],
                         triplets_to_delete: List[Triplet], expected_delete_ginfo: Dict[int, Dict[str, bool]],
                         expected_final_count: Dict[str, int], expected_delete_vinfo: Dict[int, Dict[str, bool]],
                         graph_model: GraphModel):
    graph_model.clear()
    real_create_info = graph_model.create_triplets(init_triplets, batch_size=1)

    #
    assert real_create_info.keys() == expected_create_info.keys()
    for n_type, real_nids in real_create_info['nodes'].items():
        assert expected_create_info['nodes'].get(n_type, set()) == real_nids
    for r_type, real_tids in real_create_info['triplets'].items():
        assert expected_create_info['triplets'].get(r_type, set()) == real_tids

    #
    real_items_count = graph_model.count_items()
    assert real_items_count.keys() == expected_init_count.keys()
    for expexted_k, expected_val in expected_init_count.items():
        assert real_items_count[expexted_k] == expected_val

    real_gdb_dinfo, real_vdb_dinfo = graph_model.delete_triplets(triplets_to_delete)

    #
    assert real_gdb_dinfo.keys() == expected_delete_ginfo.keys()
    for expexted_k, expected_val in expected_delete_ginfo.items():
        assert real_gdb_dinfo[expexted_k].keys() == expected_val.keys()
        for expected_k2, expected_val2 in expected_val.items():
            assert real_gdb_dinfo[expexted_k][expected_k2] == expected_val2

    #
    assert real_vdb_dinfo.keys() == expected_delete_vinfo.keys()
    for expexted_k, expected_val in expected_delete_vinfo.items():
        assert real_vdb_dinfo[expexted_k].keys() == expected_val.keys()
        for expected_k2, expected_val2 in expected_val.items():
            assert real_vdb_dinfo[expexted_k][expected_k2] == expected_val2

    #
    real_items_count = graph_model.count_items()
    assert real_items_count.keys() == expected_final_count.keys()
    for expexted_k, expected_val in expected_final_count.items():
        assert real_items_count[expexted_k] == expected_val

    #
    for i, triplet in enumerate(triplets_to_delete):
        assert not graph_model.db_conn.item_exist(triplet.id, id_type='triplet')
        if real_gdb_dinfo[i]['s_node']:
            assert not graph_model.db_conn.item_exist(triplet.start_node.get_info(), id_type='node')
        if real_gdb_dinfo[i]['e_node']:
            assert not graph_model.db_conn.item_exist(triplet.end_node.get_info(), id_type='node')

    graph_model.clear()
