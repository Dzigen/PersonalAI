import sys
# TO CHANGE
PROJECT_BASE_DIR = '../'
sys.path.insert(0, PROJECT_BASE_DIR)

from src.utils.data_structs import BaseConfigOperations

from .cases import LOAD_FULL_TEST_CASES, LOAD_PARTIAL_TEST_CASES
import pytest

@pytest.mark.parametrize("config_class, nest_category", LOAD_FULL_TEST_CASES)
def test_load_full_config(config_class: BaseConfigOperations, nest_category: int):
    expected_config = config_class()

    GOLDEN_CONFIGS_DIR = "integrational/utils/load_save_config/load/resources/full"
    load_config_path = f"{GOLDEN_CONFIGS_DIR}/{nest_category}/{expected_config.__class__.__name__}.yaml"
    real_config = config_class.load(load_config_path)

    assert expected_config == real_config


@pytest.mark.parametrize("config_class, nest_category", LOAD_PARTIAL_TEST_CASES)
def test_load_partial_config(config_class: BaseConfigOperations, nest_category: int):
    expected_config = config_class()

    GOLDEN_CONFIGS_DIR = "integrational/utils/load_save_config/load/resources/partial"
    load_config_path = f"{GOLDEN_CONFIGS_DIR}/{nest_category}/{expected_config.__class__.__name__}.yaml"
    real_config = config_class.load(load_config_path)

    assert expected_config == real_config
