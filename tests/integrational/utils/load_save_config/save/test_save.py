import sys
# TO CHANGE
PROJECT_BASE_DIR = '../'
sys.path.insert(0, PROJECT_BASE_DIR)

from src.utils.data_structs import BaseConfigOperations

from .cases import SAVE_TEST_CASES
import pytest
import yaml

@pytest.mark.parametrize("config_class, nest_category", SAVE_TEST_CASES)
def test_save_config(config_class: BaseConfigOperations, nest_category: int):
    config_instance = config_class()

    TMP_SAVE_CONFIGS_DIR = "integrational/utils/load_save_config/save/tmp"
    config_save_path = f"{TMP_SAVE_CONFIGS_DIR}/{nest_category}/{config_instance.__class__.__name__}.yaml"
    config_instance.save(config_save_path)

    GOLDEN_CONFIGS_DIR = "integrational/utils/load_save_config/save/resources"
    golden_config_path = f"{GOLDEN_CONFIGS_DIR}/{nest_category}/{config_instance.__class__.__name__}.yaml"

    with open(config_save_path, 'r') as f1:
        real_config = yaml.safe_load(f1)
    with open(golden_config_path, 'r') as f2:
        expected_config = yaml.safe_load(f2)
    assert real_config == expected_config
