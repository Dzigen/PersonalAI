from typing import Dict, List, Tuple
import pytest
import sys
sys.path.insert(0, "../")

from src.TextIdStore import TextIdStore
from src.utils import Triplet

from .cases import STORE_POPULATED_CLEARINFO_TEST_CASES

@pytest.mark.parametrize("save_info, text_id, expected_deleted_tripeltsid, expected_updated_tripeltsid, exception, textidstore_instance",
                         STORE_POPULATED_CLEARINFO_TEST_CASES, indirect=['textidstore_instance'])
def test_clearinfo(save_info: List[Tuple[str, List[Triplet]]], text_id: str,
                       expected_deleted_tripeltsid: List[str], expected_updated_tripeltsid: List[str],
                       exception: bool, textidstore_instance: TextIdStore):
    textidstore_instance.clear_store()

    for cur_textid, cur_triplets in save_info:
        textidstore_instance.save_info(cur_textid, cur_triplets)

    try:
        real_deleted_tripletsid, real_updated_tripletsid = textidstore_instance.clear_info(text_id)
    except (TypeError, ValueError) as e:
        print(str(e))
        assert exception
    else:
        assert not exception

        assert not textidstore_instance.textid_to_tripletsid_store.item_exist(text_id)
        assert real_deleted_tripletsid == expected_deleted_tripeltsid
        for triplet_id in expected_deleted_tripeltsid:
            assert not textidstore_instance.tripletid_to_textsid_store.item_exist(triplet_id)

        assert real_updated_tripletsid == expected_updated_tripeltsid
        for triplet_id in expected_updated_tripeltsid:
            real_textsid_by_tripletid = textidstore_instance.load_textsinfo_by_tripletid(triplet_id)
            assert text_id not in real_textsid_by_tripletid
