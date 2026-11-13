import pytest

import sys
sys.path.insert(0, "../")

from typing import Union, Dict

from src.environment.EnvironmentUtils import EnvironmentUtils
from src.main import PersonalAIConfig, AgentStatAnalyzerConfig, KeyValueDriverConfig

from .conftest import clear_tests_ie_output, clear_tests_ss_output
from .cases import LOAD_SETTING_OUTPUT_TEST_CASE8, LOAD_SETTING_OUTPUT_TEST_CASE9, \
    LOAD_SETTING_OUTPUT_TEST_CASE10, LOAD_SETTING_OUTPUT_TEST_CASE11, \
        PREPATE_SETTING_TEST_CASES, SEVE_SETTING_TEST_CASES

clear_tests_ie_output()
clear_tests_ss_output()

@pytest.mark.parametrize("pai_base_path, pai_name, is_exception_expected, expected_is_env_valid", [
    # 1. неверный тип данных аргументов
    (123, None, True, None),
    # 2. заданной среды не существует
    ("not/existing/path", "personalai_env", True, None),
    ("unit/utils/environment_utils/tests_input", "personalai_env", True, None),
    # 3. в заданной среде отсутствуют все директории
    ("unit/utils/environment_utils/tests_input", "personalai_env_ve4", False, False),
    # 4. в заданной среде отсутствуют все конфигурационные файлы
    ("unit/utils/environment_utils/tests_input", "personalai_env_ve5", False, False),
    # 5. в заданной среде отсутствуют все опциональные файлы
    ("unit/utils/environment_utils/tests_input", "personalai_env_ve6", False, True),
    # 6. все директории и конфигурационные файлы в заданной среде присутствуют
    ("unit/utils/environment_utils/tests_input", "personalai_env_ve7", False, True)
])
def test_validate_environment(
    pai_base_path: str, pai_name: str, 
    is_exception_expected: bool, expected_is_env_valid: bool):

    try:
        real_is_env_valid, validation_info = EnvironmentUtils.validate_environment(pai_base_path, pai_name)
        #print(validation_info)
    except (TypeError, ValueError, RuntimeError) as e:
        assert is_exception_expected
    else:
        assert not is_exception_expected
        assert expected_is_env_valid == real_is_env_valid

@pytest.mark.parametrize("pai_base_path, pai_name, is_exception_expected, expected_is_environment_exists", [
    # 1. неверный тип данных аргументов
    (213, True, True, None),
    # 2. заданной среды не существует
    ("unit/utils/environment_utils/tests_input", "notexisting_personalai_env", False, False),
    # 3. заданная среда существует
    ("unit/utils/environment_utils/tests_input", "personalai_env_fe_t3", False, True),
    # 4. в файловой системе отсутствует заданный 'pai_base_path'-путь
    ("not/existing/path", "personalai_env", False, False),
    # 5. проверить файловую систему заданной существующей среды на соответствие требованиям
    # 5.1 отсутствуют опциональные конфигурационные файлы (cache-, infstat- и qapipeline-конфиги)
    ("unit/utils/environment_utils/tests_input", "personalai_env_fe_t5", False, True),
    # 5.2 отсутствуют обязательные конфигурационные файлы (memorizepipeline- , textidstore- kgmodel-конфиги)
    ("unit/utils/environment_utils/tests_input", "personalai_env_fe_t6", True, None),
    # 5.3 отсутствуют обязательные директории
    ("unit/utils/environment_utils/tests_input", "personalai_env_fe_t7", True, None),
])
def test_find_environment(pai_base_path: str, pai_name: str, 
    is_exception_expected: bool, expected_is_environment_exists: bool):
    try:
        real_is_environment_exists = EnvironmentUtils.find_environment(pai_base_path, pai_name)
    except (TypeError, RuntimeError) as e:
        assert is_exception_expected
    else:
        assert not is_exception_expected
        assert expected_is_environment_exists == real_is_environment_exists


@pytest.mark.parametrize("pai_base_path, pai_name, is_exception_expected", [
    # 1. неверный тип данных аргументов
    (423, None, True),
    # 2. заданная среда уже существует
    ("unit/utils/environment_utils/tests_output", "personalai_env_ie_t2", True),
    # 3. заданная среда успешно создана
    ("unit/utils/environment_utils/tests_output", "personalai_env_ie_t3", False),
    # 4. в файловой системе отсутвует заданный 'pai_base_path'-путь
    ("not/existing/path", "personalai_env_ie_t4", True)
])
def test_initialize_environment(
    pai_base_path: str, pai_name: str, 
    is_exception_expected: bool):
    try:
        EnvironmentUtils.initialize_environment(pai_base_path, pai_name)
    except (TypeError, ValueError) as e:
        assert is_exception_expected
    else:
        assert not is_exception_expected
        _, validation_info = EnvironmentUtils.validate_environment(pai_base_path, pai_name)
        for dir_kw, is_dir_exists in validation_info['directories'].items():
            #print(dir_kw)
            assert is_dir_exists

@pytest.mark.parametrize("pai_base_path, pai_name, is_exception_expected, expected_output", [
    # 1. неверный тип данных аргументов
    (125, None, True, None),
    # 2. в файловой системе отсутвует заданный 'pai_base_path'-путь
    ("not/existing/path", "personalai_env_ls_t2", True, None),
    # 3. заданной среды не существует
    ("unit/utils/environment_utils/tests_input", "personalai_env_notexisting", True, None),
    # 4. в заданной среде отсутствует pai_partial_config
    ("unit/utils/environment_utils/tests_input", "personalai_env_ls4", True, None),
    # 5. в заданной среде отсутствует KnowledgeGraphModelConfig
    ("unit/utils/environment_utils/tests_input", "personalai_env_ls5", True, None),
    # 6. в заданной среде отсутствует MemPipelineConfig
    ("unit/utils/environment_utils/tests_input", "personalai_env_ls6", True, None),
    # 7. в заданной среде отсутствует TextIdStoreConfig
    ("unit/utils/environment_utils/tests_input", "personalai_env_ls7", True, None),
    # 8. в заданной среде отсутствует cache_kvdriver_config
    ("unit/utils/environment_utils/tests_input", "personalai_env_ls8", False, LOAD_SETTING_OUTPUT_TEST_CASE8),
    # 9. в заданной среде отсутствует inferencestat_config
    ("unit/utils/environment_utils/tests_input", "personalai_env_ls9", False, LOAD_SETTING_OUTPUT_TEST_CASE9),
    # 10. в заданной среде отсутствует QAPipelineConfig
    ("unit/utils/environment_utils/tests_input", "personalai_env_ls10", False, LOAD_SETTING_OUTPUT_TEST_CASE10),
    # 11. в существующей среде все конфигурационные файлы для PersonalAI присутствуют
    ("unit/utils/environment_utils/tests_input", "personalai_env_ls11", False, LOAD_SETTING_OUTPUT_TEST_CASE11),
])
def test_load_setting(
    pai_base_path: str, pai_name: str, 
    is_exception_expected: bool, expected_output):

    try:
        real_config, real_cache_kvdriver_config, real_inferencestat_config  = EnvironmentUtils.load_setting(pai_base_path, pai_name)
    except (TypeError, ValueError, FileNotFoundError, RuntimeError) as e:
        assert is_exception_expected
    else:
        assert not is_exception_expected
        expected_config, expected_cache_kvdriver_config, expected_inferencestat_config = expected_output

        assert expected_config == real_config
        assert expected_cache_kvdriver_config == real_cache_kvdriver_config
        assert expected_inferencestat_config == real_inferencestat_config

@pytest.mark.parametrize(
        "config, cache_kvdriver_config, inferencestat_config, is_exception_expected, expected_output", 
        PREPATE_SETTING_TEST_CASES)
def test_prepare_setting(
    config: PersonalAIConfig, cache_kvdriver_config: Union[None, KeyValueDriverConfig], 
    inferencestat_config: Union[None, AgentStatAnalyzerConfig], is_exception_expected: bool, expected_output):
    try:
        real_config, real_cache_kvdriver_config, real_inferencestat_config  = EnvironmentUtils.prepare_setting(
            config, cache_kvdriver_config, inferencestat_config)
    except (TypeError, ValueError, RuntimeError) as e:
        assert is_exception_expected
    else:
        assert not is_exception_expected
        expected_config, expected_cache_kvdriver_config, expected_inferencestat_config = expected_output

        assert expected_cache_kvdriver_config == real_cache_kvdriver_config
        assert expected_inferencestat_config == real_inferencestat_config
        assert expected_config == real_config

@pytest.mark.parametrize(
        "config, cache_kvdriver_config, inferencestat_config, is_init_env, is_exception_expected, expected_files_info", 
        SEVE_SETTING_TEST_CASES)
def test_save_setting(
    config: PersonalAIConfig, cache_kvdriver_config: Union[None, KeyValueDriverConfig], 
    inferencestat_config: Union[None, AgentStatAnalyzerConfig], is_init_env: bool, is_exception_expected: bool, 
    expected_files_info: Dict[str, Dict[str, bool]]):
    if is_init_env:
        EnvironmentUtils.initialize_environment(config.pai_base_path, config.pai_name)
    try:
        EnvironmentUtils.save_setting(config, cache_kvdriver_config, inferencestat_config)
    except (TypeError, ValueError, RuntimeError, FileNotFoundError) as e:
        assert is_exception_expected
    else:
        assert not is_exception_expected
        is_env_valid, real_validation_info = EnvironmentUtils.validate_environment(config.pai_base_path, config.pai_name)
        assert is_env_valid
        for file_type, expected_group_info in expected_files_info.items():
            for file_name, expected_is_file_exists in expected_group_info.items():
                assert expected_is_file_exists == real_validation_info['configuration_files'][file_type][file_name]

        loaded_config, loaded_cache_kvdriver_config, loaded_inferencestat_config = \
            EnvironmentUtils.load_setting(config.pai_base_path, config.pai_name)
        assert config == loaded_config
        assert cache_kvdriver_config == loaded_cache_kvdriver_config
        assert inferencestat_config == loaded_inferencestat_config