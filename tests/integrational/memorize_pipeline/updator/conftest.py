import pytest

import sys
# TO CHANGE
PROJECT_BASE_DIR = '../..'
sys.path.insert(0, PROJECT_BASE_DIR)

@pytest.fixture(scope='package')
def kg_model():
    # TODO
    pass

@pytest.fixture(scope='package')
def llm_updator():
    # TODO
    pass
