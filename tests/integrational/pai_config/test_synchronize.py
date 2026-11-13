import pytest

import sys
sys.path.insert(0, "../")

from typing import Union

from src.main import PersonalAIConfig, AgentStatAnalyzerConfig, KeyValueDriverConfig
from src.environment.config import PAI_FILESTRUCTURE

@pytest.mark.parametrize("cache_kvdriver_config, pai_config, is_exception_expected", [
    # 1. неверный тип данных
    ("bad cache_kvdriver_config", PersonalAIConfig(), True),
    # 2. изменён только базовый путь до хранилища данных 
    (KeyValueDriverConfig(), PersonalAIConfig(kg_related_database_name='DefaultPersonalAIKVDB'), False),
    # 3. изменён базовый путь до хранилища данных и название бд
    (KeyValueDriverConfig(), PersonalAIConfig(), False)
])
def test_synchronize_cache_kvdriver_config(
    cache_kvdriver_config: KeyValueDriverConfig,
    pai_config: PersonalAIConfig,
    is_exception_expected: bool):

    try:
        pai_config.synchronize_cache_kvdriver_config(cache_kvdriver_config)
    except TypeError:
        assert is_exception_expected
    else:
        assert not is_exception_expected
        assert pai_config.kg_related_database_name == cache_kvdriver_config.db_config.db_info['db']
        expected_cache_path = f"{pai_config.pai_base_path}/{pai_config.pai_name}/{PAI_FILESTRUCTURE['directories']['cache']}"
        assert expected_cache_path == cache_kvdriver_config.db_config.db_info['expected_db_base_path']


@pytest.mark.parametrize("inferencestat_config, pai_config, is_exception_expected", [
    # 1. неверный тип данных
    ("bad inferencestat_config", PersonalAIConfig(), True),
    # 2. изменён только базовый путь до хранилища данных 
    (AgentStatAnalyzerConfig(), PersonalAIConfig(kg_related_database_name='DefaultPersonalAITableDB'), False),
    # 3. изменён базовый путь до хранилища данных и название бд
    (AgentStatAnalyzerConfig(), PersonalAIConfig(), False)
])
def test_synchronize_inferencestat_config(
    inferencestat_config: AgentStatAnalyzerConfig,
    pai_config: PersonalAIConfig, is_exception_expected: bool):
    try:
        pai_config.synchronize_inferencestat_config(inferencestat_config)
    except TypeError:
        assert is_exception_expected
    else:
        assert not is_exception_expected
        assert pai_config.kg_related_database_name == inferencestat_config.table_driver_config.db_config.db_info['db']
        expected_inferencestat_path = f"{pai_config.pai_base_path}/{pai_config.pai_name}/{PAI_FILESTRUCTURE['directories']['agent_stat']}"
        assert expected_inferencestat_path == inferencestat_config.table_driver_config.db_config.db_info['expected_db_base_path']


# !!! PAY ATTENTION !!!
# pai_name-, pai_base_path-, kg_related_database_name-fields 
# should be in an appropriate format
# !!! PAY ATTENTION !!!

@pytest.mark.parametrize("pai_base_path, pai_name, kg_related_database_name, pai_config", [
    # 1. конфиг остался прежним: использованы значения по умолчанию
    (None, None, None, PersonalAIConfig()),
    # 2. изменено только pai_name-поле во всех дочернинх конфигах
    (None, None, None, PersonalAIConfig(pai_name="test pai_name")),
    # 3. изменено только pai_base_path-поле во всех дочернинх конфигах
    (None, None, None, PersonalAIConfig(pai_base_path="test pai_base_name")),
    # 4. изменено только kg_related_database_name-поле во всех дочернинх конфигах
    (None, None, None, PersonalAIConfig(kg_related_database_name="TestDBName")),
    # 5. изменены все environment-поля во всех дочернинх конфигах
    (None, None, None, PersonalAIConfig(
        pai_name="test pai_name", pai_base_path="test pai_base_name", 
        kg_related_database_name="TestDBName")),
    # 6. для изменения всех environment-полей используются аргументы synchronize-метода
    ("test pai_base_name", "test pai_name", "TestDBName", PersonalAIConfig())
])
def test_synchronize_environment(
    pai_base_path: str, pai_name: str, 
    kg_related_database_name: str, pai_config: PersonalAIConfig):

    pai_config.synchronize_environment(pai_base_path, pai_name, kg_related_database_name)

    expected_pai_base_path = pai_config.pai_base_path if pai_base_path is None else pai_base_path
    assert expected_pai_base_path == pai_config.pai_base_path
    assert expected_pai_base_path == pai_config.kg_model_config.pai_base_path
    assert expected_pai_base_path == pai_config.kg_model_config.graph_embeddings_config.pai_base_path
    assert expected_pai_base_path == pai_config.kg_model_config.graph_struct_config.pai_base_path
    assert expected_pai_base_path == pai_config.textidstore_config.pai_base_path
    
    expected_pai_name = pai_config.pai_name if pai_name is None else pai_name
    assert expected_pai_name == pai_config.pai_name
    assert expected_pai_name == pai_config.kg_model_config.pai_name
    assert expected_pai_name == pai_config.kg_model_config.graph_embeddings_config.pai_name
    assert expected_pai_name == pai_config.kg_model_config.graph_struct_config.pai_name
    assert expected_pai_name == pai_config.textidstore_config.pai_name
    
    expected_kg_related_database_name = pai_config.kg_related_database_name if kg_related_database_name is None else kg_related_database_name
    assert expected_kg_related_database_name == pai_config.kg_related_database_name
    assert expected_kg_related_database_name == pai_config.kg_model_config.kg_related_database_name
    assert expected_kg_related_database_name == pai_config.kg_model_config.graph_embeddings_config.kg_related_database_name
    assert expected_kg_related_database_name == pai_config.kg_model_config.graph_struct_config.kg_related_database_name
    assert expected_kg_related_database_name == pai_config.textidstore_config.kg_related_database_name


@pytest.mark.parametrize("pai_config", [
    # 1. конфиг изменён: информация по хранилищам данных отредактирована по всех дочернинх конфигах
    PersonalAIConfig()
])
def test_synchronize_databases(
    pai_config: PersonalAIConfig):
    pai_config.synchronize_environment()
    pai_config.synchronize_database()

    db_name_fields = [
        pai_config.textidstore_config.texttotriplets_store_config.db_config.db_info['db'],
        pai_config.textidstore_config.triplettotexts_store_config.db_config.db_info['db'],
        pai_config.kg_model_config.graph_struct_config.driver_config.db_config.db_info['db'],
        pai_config.kg_model_config.graph_embeddings_config.nodesdb_driver_configs_mapping['dense_nodes'].db_config.db_info['db'],
        pai_config.kg_model_config.graph_embeddings_config.nodesdb_driver_configs_mapping['bm25_nodes'].db_config.db_info['db'],
        pai_config.kg_model_config.graph_embeddings_config.tripletsdb_driver_configs_mapping['dense_triplets'].db_config.db_info['db'],
        pai_config.kg_model_config.graph_embeddings_config.tripletsdb_driver_configs_mapping['bm25_triplets'].db_config.db_info['db'],
    ]
    for cur_real_dbname in db_name_fields:
        assert pai_config.kg_related_database_name == cur_real_dbname

    db_base_path = [
        pai_config.textidstore_config.texttotriplets_store_config.db_config.db_info['expected_db_base_path'],
        pai_config.textidstore_config.triplettotexts_store_config.db_config.db_info['expected_db_base_path'],
        pai_config.kg_model_config.graph_struct_config.driver_config.db_config.db_info['expected_db_base_path'],
        pai_config.kg_model_config.graph_embeddings_config.nodesdb_driver_configs_mapping['dense_nodes'].db_config.db_info['expected_db_base_path'],
        pai_config.kg_model_config.graph_embeddings_config.nodesdb_driver_configs_mapping['bm25_nodes'].db_config.db_info['expected_db_base_path'],
        pai_config.kg_model_config.graph_embeddings_config.tripletsdb_driver_configs_mapping['dense_triplets'].db_config.db_info['expected_db_base_path'],
        pai_config.kg_model_config.graph_embeddings_config.tripletsdb_driver_configs_mapping['bm25_triplets'].db_config.db_info['expected_db_base_path'],
    ]
    for cur_real_dbname in db_name_fields:
        assert pai_config.kg_related_database_name == cur_real_dbname


@pytest.mark.parametrize("pai_config", [
    # 1. неверный тип данных
    # 2. конфиг остался прежним: использованы значения по умолчанию
    # 3. конфиг изменён: информация по местоположению файла журналирования отредактировано
    # 4. конфиг изменён: использованы значения из аргументов
])
def test_synchronize_logging(
    pai_config: PersonalAIConfig):
    # TODO
    raise NotImplementedError

@pytest.mark.parametrize("pai_config", [
    # 1. неверный тип данных
    # 2. конфиг остался прежним: использованы значения по умолчанию
    # 3. конфиг изменён: информация по языку llm-промптов отредактировано
    # 4. конфиг изменён: использовано значение из аргумента
])
def test_synchronize_language(
    pai_config: PersonalAIConfig):
    # TODO
    raise NotImplementedError