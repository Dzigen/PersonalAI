from ..cases import AVAILABLE_PAICONFIG_COMBINATIONS, \
    AVAILABLE_CACHE_DBS, AVAILABLE_AGENTSTAT_DBS, RAW_TEXTS_EN, QUESTIONS

# is_env_precreated, is_precreated_env_have_cache_config, 
# is_precreated_env_have_agentstat_config, is_load_exising_env, env_filesettings_to_delete, 
# is_exception_expected, texts, questions, language, | pai_config, cache_config, agentstat_config
ENVIRONMENT_CONNECTION_TEST_CASES = [
    # 1. Подключение к существующей среде при создании экземпляра PersonalAI-класса
    (True, True, True, True, [], False, RAW_TEXTS_EN[:2], QUESTIONS['en'][:1], 'en'),
    # 2. Создание новой среды при создании экземпляра PersonalAI-класса
    (False, None, None, False, [], False, RAW_TEXTS_EN[:2], QUESTIONS['en'][:1], 'en'),
    # 3. Указанные конфигурации при инициализации PersonalAI-класса не должны измениться 
    # в результате их внутренней адаптации/модификации для заданного экземпляра.
    # 3.1. при создании среды
    # TODO
    # 3.2. при подключении к существующей среде
    # TODO
    # 5. В существующей среде отсутствует конфигурация QA-пайплайна
    (True, True, True, True, [('optional', 'qa_pipeline_config')], False, RAW_TEXTS_EN[:2], QUESTIONS['en'][:1], 'en'),
    # 6. В существующей среде отсутствует partial_pai-конфигурация 
    (True, True, True, True, [('required', 'personalai_partial_config')], True, RAW_TEXTS_EN[:2], QUESTIONS['en'][:1], 'en'),
    # 7. В существующей среде отсутствует конфигурация Memorize-пайплайна
    (True, True, True, True, [('required', 'mem_pipeline_config')], True, RAW_TEXTS_EN[:2], QUESTIONS['en'][:1], 'en'),
    # 8. В существующей среде отсутствует конфигурация KnowledgeGraphModel-конфигурация
    (True, True, True, True, [('required', 'kg_model_config')], True, RAW_TEXTS_EN[:2], QUESTIONS['en'][:1], 'en'),
    # 9. В существующей среде отсутствует конфигурация TextIdStore-конфигурация
    (True, True, True, True, [('required', 'textidstore_config')], True, RAW_TEXTS_EN[:2], QUESTIONS['en'][:1], 'en'),
    # 10. Во время создания среды не были указаны cache_kvdriver_config и inferencestat_config, 
    # а при повторном обращении к среде они указаны были
    (True, False, False, True, [], False, RAW_TEXTS_EN[:2], QUESTIONS['en'][:1], 'en')
]

POPULATED_ENVIRONMENT_CONNECTION_TEST_CASES = []
for case in ENVIRONMENT_CONNECTION_TEST_CASES:
    for pai_vendors in AVAILABLE_PAICONFIG_COMBINATIONS:
        pai_kw = "/".join(pai_vendors)
        for cache_vendor in AVAILABLE_CACHE_DBS:
            for agentstat_vendor in AVAILABLE_AGENTSTAT_DBS:
                POPULATED_ENVIRONMENT_CONNECTION_TEST_CASES.append(
                    case + (pai_kw, cache_vendor, agentstat_vendor))