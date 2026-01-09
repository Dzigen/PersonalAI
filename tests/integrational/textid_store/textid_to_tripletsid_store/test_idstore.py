from typing import Dict, List, Tuple
import pytest
import sys
sys.path.insert(0, "../")

from src.TextIdStore import TextIdStore
from src.utils import Triplet

from .cases import STORE_POPULATED_SAVE_TEST_CASES, STORE_POPULATED_LOAD_TEST_CASES


@pytest.mark.parametrize("save_info, text_id, expected_triplets, exception, textidstore_instance",
                         STORE_POPULATED_SAVE_TEST_CASES,
                         indirect=['textidstore_instance'])
def test_save_tripletsinfo_by_textid(save_info: List[Tuple[str, List[Triplet]]], text_id: str,
                       expected_triplets: List[Triplet], exception: bool,
                       textidstore_instance: TextIdStore):
    textidstore_instance.clear_store()

    try:
        for cur_textid, cur_triplets in save_info:
            textidstore_instance.save_tripletsinfo_by_textid(cur_textid, cur_triplets)
    except (TypeError, ValueError) as e:
        print(str(e))
        assert exception
    else:
        assert not exception

        real_triplets_info = textidstore_instance.load_tripletsinfo_by_textid(text_id)
        expected_triplets_map = {triplet.id: triplet for triplet in expected_triplets}
        assert len(real_triplets_info) == len(expected_triplets)
        for real_triplet in real_triplets_info:
            expected_triplet = expected_triplets_map.get(real_triplet.id, None)
            assert expected_triplet is not None
            assert real_triplet.start_node.id == expected_triplet.start_node.id
            assert real_triplet.start_node.type == expected_triplet.start_node.type
            assert real_triplet.relation.id == expected_triplet.relation.id
            assert real_triplet.relation.type == expected_triplet.relation.type
            assert real_triplet.end_node.id == expected_triplet.end_node.id
            assert real_triplet.end_node.type == expected_triplet.end_node.type


@pytest.mark.parametrize("save_info, text_id, expected_triplets, exception, textidstore_instance",
                         STORE_POPULATED_LOAD_TEST_CASES,
                         indirect=['textidstore_instance'])
def test_load_tripletsinfo_by_textid(save_info: List[Tuple[str, List[Triplet]]], text_id: str,
                         expected_triplets: List[Triplet], exception: bool,
                         textidstore_instance: TextIdStore):
    textidstore_instance.clear_store()

    for cur_textid, cur_triplets in save_info:
        textidstore_instance.save_tripletsinfo_by_textid(cur_textid, cur_triplets)

    try:
        real_triplets_info = textidstore_instance.load_tripletsinfo_by_textid(text_id)
    except (TypeError, ValueError) as e:
        print(str(e))
        assert exception
    else:
        assert not exception

        expected_triplets_map = {triplet.id: triplet for triplet in expected_triplets}
        assert len(real_triplets_info) == len(expected_triplets)
        for real_triplet in real_triplets_info:
            expected_triplet = expected_triplets_map.get(real_triplet.id, None)
            assert expected_triplet is not None
            assert real_triplet.start_node.id == expected_triplet.start_node.id
            assert real_triplet.start_node.type == expected_triplet.start_node.type
            assert real_triplet.relation.id == expected_triplet.relation.id
            assert real_triplet.relation.type == expected_triplet.relation.type
            assert real_triplet.end_node.id == expected_triplet.end_node.id
            assert real_triplet.end_node.type == expected_triplet.end_node.type
