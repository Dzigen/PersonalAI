import pytest

from cases import GM_CREATE_TESTS, GM_DELETE_TESTS

@pytest.mark.parametrize("triplets, expected", GM_CREATE_TESTS)
def test_create_triplets(triplets, expected, graph_model):
    # TODO
    pass

@pytest.mark.parametrize("triplet_ids, expected", GM_DELETE_TESTS)
def test_delete_triplets(graph_model):
    # TODO
    pass
