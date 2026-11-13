import sys
sys.path.insert(0, "../")

from copy import deepcopy

from src.main import PersonalAIConfig, AgentStatAnalyzerConfig, DEFAULT_PERSONALAI_KVCACHE_CONFIG, KeyValueDriverConfig
from src.PersonalAIConfig import KnowledgeGraphModelConfig, TextIdStoreConfig, QAPipelineConfig, MemPipelineConfig
from src.pipelines.qa.query_preprocessing.QueryPreprocessor import QueryPreprocessorConfig, QueryEnhancerConfig
from src.db_drivers.kv_driver.configs import DEFAULT_REDISKV_CONFIG

LOAD_SETTING_OUTPUT_TEST_CASE8 = (
    PersonalAIConfig(
        qa_pipeline_config=QAPipelineConfig(
            preprocessor_config=QueryPreprocessorConfig(
                enhancing_config=QueryEnhancerConfig()
            )
        )
    ),
    None,
    AgentStatAnalyzerConfig()
)

LOAD_SETTING_OUTPUT_TEST_CASE9 = (
    PersonalAIConfig(
        qa_pipeline_config=QAPipelineConfig(
            preprocessor_config=QueryPreprocessorConfig(
                enhancing_config=QueryEnhancerConfig()
            )
        )
    ),
    DEFAULT_PERSONALAI_KVCACHE_CONFIG,
    None
)

LOAD_SETTING_OUTPUT_TEST_CASE10 = (
    PersonalAIConfig(),
    DEFAULT_PERSONALAI_KVCACHE_CONFIG,
    AgentStatAnalyzerConfig()
)

LOAD_SETTING_OUTPUT_TEST_CASE11 = (
    PersonalAIConfig(
        qa_pipeline_config=QAPipelineConfig(
            preprocessor_config=QueryPreprocessorConfig(
                enhancing_config=QueryEnhancerConfig()
            )
        )
    ),
    DEFAULT_PERSONALAI_KVCACHE_CONFIG,
    AgentStatAnalyzerConfig()
)

# ===========================================

PS_PAICONFIG_V1 = PersonalAIConfig(
    pai_base_path="unit/utils/environment_utils/tests_input",
    pai_name="personalai_env_ps2",
    kg_model_config=KnowledgeGraphModelConfig(
        pai_base_path="unit/utils/environment_utils/tests_input",
        pai_name="personalai_env_ps2"
    ),
    textidstore_config=TextIdStoreConfig(
        pai_base_path="unit/utils/environment_utils/tests_input",
        pai_name="personalai_env_ps2"    
    )
)
PS_EXPECTED_OUTPUT_CASE2 = (deepcopy(PS_PAICONFIG_V1), None, AgentStatAnalyzerConfig())


PS_PAICONFIG_V2 = PersonalAIConfig(
    pai_base_path="unit/utils/environment_utils/tests_input",
    pai_name="personalai_env_ps3",
    kg_model_config=KnowledgeGraphModelConfig(
        pai_base_path="unit/utils/environment_utils/tests_input",
        pai_name="personalai_env_ps3"
    ),
    textidstore_config=TextIdStoreConfig(
        pai_base_path="unit/utils/environment_utils/tests_input",
        pai_name="personalai_env_ps3"    
    )
)
PS_EXPECTED_OUTPUT_CASE3 = (deepcopy(PS_PAICONFIG_V2), deepcopy(DEFAULT_PERSONALAI_KVCACHE_CONFIG), None)

PS_PAICONFIG_V3 = PersonalAIConfig(
    mem_pipeline_config=MemPipelineConfig(
        lang='ru'
    ),
    qa_pipeline_config=QAPipelineConfig(
        lang='ru'
    ),
    textidstore_config=TextIdStoreConfig(
        verbose=True,
        kg_related_database_name="test_name",
        pai_base_path="unit/utils/environment_utils/tests_input",
        pai_name="personalai_env_ps4"
    ),
    kg_model_config=KnowledgeGraphModelConfig(
        kg_related_database_name="test_name",
        verbose=True,
        pai_base_path="unit/utils/environment_utils/tests_input",
        pai_name="personalai_env_ps4"
    ),
    pai_base_path="unit/utils/environment_utils/tests_input",
    pai_name="personalai_env_ps4" 
)
PS_EXPECTED_PAICONFIG_CASE4 = PersonalAIConfig(
    textidstore_config=TextIdStoreConfig(
        pai_base_path="unit/utils/environment_utils/tests_input",
        pai_name="personalai_env_ps4"
    ),
    kg_model_config=KnowledgeGraphModelConfig(
        pai_base_path="unit/utils/environment_utils/tests_input",
        pai_name="personalai_env_ps4"
    ),
    pai_base_path="unit/utils/environment_utils/tests_input",
    pai_name="personalai_env_ps4" 
)
PS_EXPECTED_OUTPUT_CASE4 = (PS_EXPECTED_PAICONFIG_CASE4, None, None)

PS_PAICONFIG_V4 = PersonalAIConfig(
    mem_pipeline_config=MemPipelineConfig(
        lang='ru'
    ),
    textidstore_config=TextIdStoreConfig(
        verbose=True,
        kg_related_database_name="test_name",
        pai_base_path="unit/utils/environment_utils/tests_input",
        pai_name="personalai_env_ps5"
    ),
    kg_model_config=KnowledgeGraphModelConfig(
        kg_related_database_name="test_name",
        verbose=False,
        pai_base_path="unit/utils/environment_utils/tests_input",
        pai_name="personalai_env_ps5"
    ),
    pai_base_path="unit/utils/environment_utils/tests_input",
    pai_name="personalai_env_ps5" 
)
PS_EXPECTED_PAICONFIG_CASE5 = PersonalAIConfig(
    textidstore_config=TextIdStoreConfig(
        pai_base_path="unit/utils/environment_utils/tests_input",
        pai_name="personalai_env_ps5"
    ),
    kg_model_config=KnowledgeGraphModelConfig(
        pai_base_path="unit/utils/environment_utils/tests_input",
        pai_name="personalai_env_ps5"
    ),
    pai_base_path="unit/utils/environment_utils/tests_input",
    pai_name="personalai_env_ps5" 
)

PS_EXPECTED_OUTPUT_CASE5 = (PS_EXPECTED_PAICONFIG_CASE5, None, None)

PS_PAICONFIG_V5 = PersonalAIConfig(
    pai_base_path="unit/utils/environment_utils/tests_input",
    pai_name="personalai_env_ps6",
    kg_model_config=KnowledgeGraphModelConfig(
        pai_base_path="unit/utils/environment_utils/tests_input",
        pai_name="personalai_env_ps6"
    ),
    textidstore_config=TextIdStoreConfig(
        pai_base_path="unit/utils/environment_utils/tests_input",
        pai_name="personalai_env_ps6"    
    )
)
PS_KVCACHECONFIG_V1 = KeyValueDriverConfig(
    db_config=DEFAULT_REDISKV_CONFIG,
    db_vendor='redis'
)
PS_AGENTSTATCONFIG_V1 = AgentStatAnalyzerConfig(
    column_info=[]
)
PS_EXPECTED_OUTPUT_CASE6 = (PS_PAICONFIG_V5, deepcopy(DEFAULT_PERSONALAI_KVCACHE_CONFIG), AgentStatAnalyzerConfig())

PS_PAICONFIG_V6 = PersonalAIConfig(
    pai_base_path="unit/utils/environment_utils/tests_input",
    pai_name="personalai_env_ps7",
    kg_model_config=KnowledgeGraphModelConfig(
        pai_base_path="unit/utils/environment_utils/tests_input",
        pai_name="personalai_env_ps7"
    ),
    textidstore_config=TextIdStoreConfig(
        pai_base_path="unit/utils/environment_utils/tests_input",
        pai_name="personalai_env_ps7"    
    )
)
PS_EXPECTED_OUTPUT_CASE7 = (PS_PAICONFIG_V6, deepcopy(PS_KVCACHECONFIG_V1), deepcopy(PS_AGENTSTATCONFIG_V1))

# config: PersonalAIConfig, cache_kvdriver_config: Union[None, KeyValueDriverConfig], 
# inferencestat_config: Union[None, AgentStatAnalyzerConfig], is_exception_expected: bool, expected_output
PREPATE_SETTING_TEST_CASES = [
    # 1. неверный тип данных аргументов
    (123, False, "test", True, None),
    # 2. в качестве cache_kvdriver_config указан None
    (PS_PAICONFIG_V1, None, AgentStatAnalyzerConfig(), False, PS_EXPECTED_OUTPUT_CASE2),
    # 3. в качетсве inferencestat_config указан None
    (PS_PAICONFIG_V2, deepcopy(DEFAULT_PERSONALAI_KVCACHE_CONFIG), None, False, PS_EXPECTED_OUTPUT_CASE3),
    # 4. редактируется весь исходный PersonalAIConfig
    (PS_PAICONFIG_V3, None, None, False, PS_EXPECTED_OUTPUT_CASE4),
    # 5. редактируется только KnowledgeGraphModelConfig, TextIdStoreConfig, MemPipelineConfig в PersonalAIConfig
    (PS_PAICONFIG_V4, None, None, False, PS_EXPECTED_OUTPUT_CASE5),
    # 6. в файловой системе среды присутствуют конфиги для кеша и сбора статистики по llm-токенам, 
    # при этом в cache_kvdriver_config и inferencestat_config указан не None
    (PS_PAICONFIG_V5, PS_KVCACHECONFIG_V1, PS_AGENTSTATCONFIG_V1, False, PS_EXPECTED_OUTPUT_CASE6),
    # 7. в файловой системе среды отсутствуют конфиги для кеша и сбора статистики по llm-токенам, 
    # при этом в cache_kvdriver_config и inferencestat_config указан не None
    (PS_PAICONFIG_V6, PS_KVCACHECONFIG_V1, PS_AGENTSTATCONFIG_V1, False, PS_EXPECTED_OUTPUT_CASE7),
]

# =====================================================

PAI_CONFIG_CASE2 = PersonalAIConfig(
    pai_base_path="not/existing/path" 
)

PAI_CONFIG_CASE3 = PersonalAIConfig(
    pai_base_path="unit/utils/environment_utils/tests_output",
    pai_name="personalai_env_notexisting"  
)

PAI_CONFIG_CASE4 = PersonalAIConfig(
    pai_base_path="unit/utils/environment_utils/tests_output",
    pai_name="personalai_env_ss_t4"  
)
EXPECTED_FILES_INFO_CASE4 = {
    'required': {
        'personalai_partial_config': True,
        'kg_model_config': True,
        'mem_pipeline_config': True,
        'textidstore_config': True
    },
    'optional': {
        'qa_pipeline_config': True,
        'cache_kvdriver_config': False,
        'inferencestat_config': True
    }
}

PAI_CONFIG_CASE5 = PersonalAIConfig(
    pai_base_path="unit/utils/environment_utils/tests_output",
    pai_name="personalai_env_ss_t5"  
)
EXPECTED_FILES_INFO_CASE5 = {
    'required': {
        'personalai_partial_config': True,
        'kg_model_config': True,
        'mem_pipeline_config': True,
        'textidstore_config': True
    },
    'optional': {
        'qa_pipeline_config': True,
        'cache_kvdriver_config': True,
        'inferencestat_config': False
    }
}

PAI_CONFIG_CASE6 = PersonalAIConfig(
    pai_base_path="unit/utils/environment_utils/tests_output",
    pai_name="personalai_env_ss_t6"  
)
EXPECTED_FILES_INFO_CASE6 = {
    'required': {
        'personalai_partial_config': True,
        'kg_model_config': True,
        'mem_pipeline_config': True,
        'textidstore_config': True
    },
    'optional': {
        'qa_pipeline_config': True,
        'cache_kvdriver_config': True,
        'inferencestat_config': True
    }
}

#config: PersonalAIConfig, cache_kvdriver_config: Union[None, KeyValueDriverConfig], 
# inferencestat_config: Union[None, AgentStatAnalyzerConfig], is_init_env: bool, 
# is_exception_expected: bool, expected_files_info: Dict[str, Dict[str, bool]]
SEVE_SETTING_TEST_CASES = [
    # 1. неверный тип данных аргументов
    (None, 123, "e12e", False, True, None),
    # 2. в файловой системе отсутвует заданный 'pai_base_path'-путь
    (PAI_CONFIG_CASE2, None, None, False, True, None),
    # 3. отсутствует среда по заданному пути
    (PAI_CONFIG_CASE3, None, None, False, True, None),
    # 4. в качестве cache_kvdriver_config указан None
    (PAI_CONFIG_CASE4, None, AgentStatAnalyzerConfig(), True, False, EXPECTED_FILES_INFO_CASE4),
    # 5. в качетсве inferencestat_config указан None
    (PAI_CONFIG_CASE5, deepcopy(DEFAULT_PERSONALAI_KVCACHE_CONFIG), None, True, False, EXPECTED_FILES_INFO_CASE5),
    # 6. успешное сохранение всех конфигурационных файлов PersonalAI в файловую систему соответствующей среды
    (PAI_CONFIG_CASE6, deepcopy(DEFAULT_PERSONALAI_KVCACHE_CONFIG), AgentStatAnalyzerConfig(), True, False, EXPECTED_FILES_INFO_CASE6),
]