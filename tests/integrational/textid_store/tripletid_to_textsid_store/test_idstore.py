from typing import Dict, List, Tuple, Set
import pytest
from collections import defaultdict
import sys
sys.path.insert(0, "../")

from src.TextIdStore import TextIdStore
from src.utils import Triplet

from .cases import STORE_POPULATED_SAVE_TEST_CASES, STORE_POPULATED_LOAD_TEST_CASES


@pytest.mark.parametrize("save_info, expected_triplettotexts_map, exception, textidstore_instance",
                         STORE_POPULATED_SAVE_TEST_CASES, indirect=['textidstore_instance'])
def test_save_textsinfo_by_tripletid(save_info: List[Tuple[str, List[Triplet]]],
                       expected_triplettotexts_map: Dict[str, List[str]], exception: bool,
                       textidstore_instance: TextIdStore):
    textidstore_instance.clear_store()

    try:
        for cur_textid, cur_triplets in save_info:
            textidstore_instance.save_textinfo_by_triplets(cur_textid, cur_triplets)
    except (TypeError, ValueError) as e:
        print(str(e))
        assert exception
    else:
        assert not exception

        real_triplettotexts_map = dict()
        for cur_textid, cur_triplets in save_info:
            for cur_triplet in cur_triplets:
                real_triplettotexts_map[cur_triplet.id] = textidstore_instance.load_textsinfo_by_tripletid(cur_triplet.id)

        assert expected_triplettotexts_map == real_triplettotexts_map

@pytest.mark.parametrize("save_info, triplet_id, expected_texts_info, exception, textidstore_instance",
                         STORE_POPULATED_LOAD_TEST_CASES, indirect=['textidstore_instance'])
def test_load_textsinfo_by_tripletid(save_info: List[Tuple[str, List[Triplet]]],
                         triplet_id: str, expected_texts_info: Set[str], exception: bool,
                         textidstore_instance: TextIdStore):
    textidstore_instance.clear_store()

    for cur_textid, cur_triplets in save_info:
        textidstore_instance.save_textinfo_by_triplets(cur_textid, cur_triplets)

    try:
        real_texts_info = textidstore_instance.load_textsinfo_by_tripletid(triplet_id)
    except (TypeError, ValueError) as e:
        print(str(e))
        assert exception
    else:
        assert not exception
        assert real_texts_info == expected_texts_info
