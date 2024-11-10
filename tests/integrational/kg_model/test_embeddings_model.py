import pytest

import sys
sys.path.insert(0, "../../")
import pytest

from cases import EM_CREATE_TESTS, EM_DELETE_TESTS

@pytest.mark.parametrize("triplets, expected", EM_CREATE_TESTS)
def test_create_triplets(embeddings_model):
    # TODO
    pass

@pytest.mark.parametrize("triplets, expected", EM_DELETE_TESTS)
def test_delete_triplets(embeddings_model):
    # TODO
    pass
