import pytest
from typing import Dict
from copy import deepcopy
import sys
import shutil
import os
import pandas as pd
sys.path.insert(0, "../")

from typing import List, Union

from src.main import PersonalAIConfig, AgentStatAnalyzerConfig, KeyValueDriverConfig, PersonalAI
from src.environment.config import PAI_FILESTRUCTURE

from .cases import POPULATED_ENVIRONMENT_CONNECTION_TEST_CASES
from ..conftest import clear_tests_output

clear_tests_output()

def flat_dict(nested_dict: Dict) -> Dict[str, object]:
    df = pd.json_normalize(nested_dict, sep='_')
    flat_dict: Dict = df.to_dict(orient='records')[0]
    return flat_dict

@pytest.mark.parametrize(
    "is_env_precreated, is_precreated_env_have_cache_config, \
        is_precreated_env_have_agentstat_config, is_load_exising_env, env_filesettings_to_delete, \
            is_exception_expected, texts, questions, language, pai_config, cache_config, agentstat_config", 
    POPULATED_ENVIRONMENT_CONNECTION_TEST_CASES, 
    indirect=['pai_config', 'cache_config', 'agentstat_config']
)
def test_environment_connection(
    is_env_precreated: bool, is_precreated_env_have_cache_config: bool,
    is_precreated_env_have_agentstat_config: bool, is_load_exising_env: bool, 
    env_filesettings_to_delete: List[str], is_exception_expected: bool, 
    texts: List[str], questions: List[str], language: str, pai_config: PersonalAIConfig, 
    cache_config: Union[None, KeyValueDriverConfig], agentstat_config: Union[None, AgentStatAnalyzerConfig]):

    # 
    preenv_name: str = None
    preenv_kgmodel_itemscount: Dict = None
    preenv_textidstore_itemscount: Dict = None
    preenv_cache_itemscount: Dict = dict()
    preenv_agentstat_itemscount: Dict = dict()
    if is_env_precreated:
        precreated_paiconfig = deepcopy(pai_config)
        precreated_paiconfig.lang = language
        precreated_paiconfig.pai_name = None
        pre_cache_config = cache_config if is_precreated_env_have_cache_config else None
        pre_agentstat_config = agentstat_config if is_precreated_env_have_agentstat_config else None

        pre_pai = PersonalAI(precreated_paiconfig, pre_cache_config, pre_agentstat_config)
        pre_pai.open_connections()
        assert pre_pai.is_connections_open()

        for text in texts:
            _, rinfo, _ = pre_pai.update_memory(text)
            assert rinfo.status.value == 0

        for question in questions:
            _, rinfo, _ = pre_pai.answer_question(question)
            assert rinfo.status.value == 0

        preenv_name = precreated_paiconfig.pai_name # !!! PAY ATTENTION
        preenv_kgmodel_itemscount = flat_dict(pre_pai.kg_model.count_items())
        preenv_textidstore_itemscount = flat_dict(pre_pai.textid_store.count_items())
        preenv_cache_itemscount['mem_pipeline'] = flat_dict(pre_pai.mem_pipeline.get_cache_stat())
        preenv_cache_itemscount['qa_pipeline'] = flat_dict(pre_pai.qa_pipeline.get_cache_stat())
        preenv_agentstat_itemscount['mem_pipeline'] = flat_dict(pre_pai.mem_pipeline.get_agent_tgen_stat())
        preenv_agentstat_itemscount['qa_pipeline'] = flat_dict(pre_pai.qa_pipeline.get_agent_tgen_stat())

        for file_to_delete in env_filesettings_to_delete:
            pai_env_path = f"{precreated_paiconfig.pai_base_path}/{precreated_paiconfig.pai_name}"
            paienv_setting_path = f"{pai_env_path}/{PAI_FILESTRUCTURE['directories']['setting']}"
            absolute_filepath = f"{paienv_setting_path}/{PAI_FILESTRUCTURE['configuration_files'][file_to_delete[0]][file_to_delete[1]]}"
            os.unlink(absolute_filepath)

        pre_pai.close_connections()
        del pre_pai

    #
    new_paiconfig = deepcopy(pai_config)
    new_paiconfig.lang = language
    new_paiconfig.load_existing_environment = is_load_exising_env
    if is_env_precreated:
        new_paiconfig.pai_name = preenv_name
    try:
        new_pai = PersonalAI(new_paiconfig, cache_config, agentstat_config)
    except (RuntimeError, ValueError, FileNotFoundError) as e:
        assert is_exception_expected
    else:
        assert not is_exception_expected
        new_pai.open_connections()
        assert new_pai.is_connections_open()

        if is_env_precreated:
            real_cache_itemscount = dict()
            real_agentstat_itemscount = dict()

            realenv_name = new_paiconfig.pai_name # !!! PAY ATTENTION
            realenv_kgmodel_itemscount = flat_dict(new_pai.kg_model.count_items())
            realenv_textidstore_itemscount = flat_dict(new_pai.textid_store.count_items())
            
            real_cache_itemscount['mem_pipeline'] = flat_dict(new_pai.mem_pipeline.get_cache_stat())
            real_cache_itemscount['qa_pipeline'] = flat_dict(new_pai.qa_pipeline.get_cache_stat())
            real_agentstat_itemscount['mem_pipeline'] = flat_dict(new_pai.mem_pipeline.get_agent_tgen_stat())
            real_agentstat_itemscount['qa_pipeline'] = flat_dict(new_pai.qa_pipeline.get_agent_tgen_stat())

            print("preenv_kgmodel_itemscount: ", preenv_kgmodel_itemscount)
            print("realenv_kgmodel_itemscount: ", realenv_kgmodel_itemscount)
            print("preenv_textidstore_itemscount: ", preenv_textidstore_itemscount)
            print("realenv_textidstore_itemscount: ", realenv_textidstore_itemscount)
            print("preenv_cache_itemscount: ", preenv_cache_itemscount)
            print("real_cache_itemscount: ", real_cache_itemscount)
            print("preenv_agentstat_itemscount: ", preenv_agentstat_itemscount)
            print("real_agentstat_itemscount: ", real_agentstat_itemscount)
            


            assert preenv_name == realenv_name
            for k,v in preenv_kgmodel_itemscount.items():
                assert v == realenv_kgmodel_itemscount[k]
            for k,v in preenv_textidstore_itemscount.items():
                assert v == realenv_textidstore_itemscount[k]

            if is_precreated_env_have_cache_config:
                for pipe_name, expected_info in preenv_cache_itemscount.items():
                    for k,v in expected_info.items():
                        assert v == real_cache_itemscount[pipe_name][k]
            else:
                for pipe_name, real_info in real_cache_itemscount.items():
                    for k,v in real_info.items():
                        # костыль
                        none_fields = [
                            'MemPipeline', 'extractor_LLMExtractor', 
                            'updator_LLMUpdator', 'kg_reasoner_KnowledgeGraphReasoner',
                            'query_preprocessor_enhancer']
                        if k in none_fields:
                            assert v is None
                        else:
                            assert v == 0

            if is_precreated_env_have_agentstat_config:
                for pipe_name, expected_info in preenv_agentstat_itemscount.items():
                    for k,v in expected_info.items():
                        assert v == real_agentstat_itemscount[pipe_name][k]
            else:
                for pipe_name, real_info in real_agentstat_itemscount.items():
                    for k,v in real_info.items():
                        if k.endswith("count") or k.endswith("count_not_null"):
                            assert v == 0
                        else:
                            assert v is None 

        new_pai.close_connections()