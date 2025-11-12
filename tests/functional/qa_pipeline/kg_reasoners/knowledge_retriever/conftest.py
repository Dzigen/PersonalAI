import pytest
import sys
from copy import deepcopy
from typing import Dict
# TO CHANGE
PROJECT_BASE_DIR = '../'
TEST_VOLUME_DIR = './volumes'
sys.path.insert(0, PROJECT_BASE_DIR)

from ..conftest import kg_model, available_kg_model, ru_kg_model, en_kg_model
