from typing import Union, Dict, Tuple
from copy import deepcopy
from dataclasses import asdict
import yaml
import os

from ..PersonalAIConfig import PersonalAIConfig
from .config import PAI_FILESTRUCTURE
from .mapping import KW_TO_CONFIGURATIONS_MAPPING
from .EnvironmentConnectionUtils import EnvironmentConnectionUtils
from ..utils.agent_stat_analyzer import AgentStatAnalyzerConfig
from ..utils.data_structs import BaseComponentConfig
from ..db_drivers.kv_driver import KeyValueDriverConfig

class EnvironmentUtils(EnvironmentConnectionUtils):

    @staticmethod
    def validate_environment(pai_base_path: str, pai_name: str) -> Tuple[bool, Dict]:
        if (type(pai_base_path) is not str) or (type(pai_name) is not str):
            raise TypeError

        pai_env_path = f"{pai_base_path}/{pai_name}"
        is_env_exists = os.path.exists(pai_env_path)
        if not is_env_exists:
            raise ValueError(f"Specified PersonalAI environment '{pai_env_path}' does not exists.")

        is_env_valid = True
        validation_info = deepcopy(PAI_FILESTRUCTURE)

        for kw, cur_dir in PAI_FILESTRUCTURE['directories'].items():
            is_curdir_exists = os.path.exists(f"{pai_env_path}/{cur_dir}")
            is_env_valid = is_curdir_exists
            validation_info['directories'][kw] = is_curdir_exists

        for kw, cur_file in PAI_FILESTRUCTURE['configuration_files']['required'].items():
            is_curfile_exists = os.path.exists(f"{pai_env_path}/{PAI_FILESTRUCTURE['directories']['setting']}/{cur_file}")
            is_env_valid = is_curfile_exists
            validation_info['configuration_files']['required'][kw] = is_curfile_exists

        for kw, cur_file in PAI_FILESTRUCTURE['configuration_files']['optional'].items():
            is_curfile_exists = os.path.exists(f"{pai_env_path}/{PAI_FILESTRUCTURE['directories']['setting']}/{cur_file}")
            validation_info['configuration_files']['optional'][kw] = is_curfile_exists

        return is_env_valid, validation_info

    @staticmethod
    def find_environment(pai_base_path: str, pai_name: str) -> bool:
        if (type(pai_base_path) is not str) or (type(pai_name) is not str):
            raise TypeError

        pai_env_path = f"{pai_base_path}/{pai_name}"
        is_env_exists = os.path.exists(pai_env_path)
        
        if is_env_exists:
            is_env_valid, validation_info = EnvironmentUtils.validate_environment(pai_base_path, pai_name)
            if not is_env_valid:
                raise RuntimeError(f"Environmnet by path '{pai_env_path}' is found, but it is not valid. Validation info: {validation_info}")

        return is_env_exists

    @staticmethod
    def initialize_environment(pai_base_path: str, pai_name: str) -> None:
        if (type(pai_base_path) is not str) or (type(pai_name) is not str):
            raise TypeError

        pai_env_path = f"{pai_base_path}/{pai_name}"
        is_env_exists = os.path.exists(pai_env_path)
        if is_env_exists:
            raise ValueError(f"Specified PersonalAI environment '{pai_env_path}' is already exists.")
        is_path_exists = os.path.exists(pai_base_path)
        if not is_path_exists:
            raise ValueError(f"Specified PersonalAI environment base path '{pai_base_path}' is not exists.")
        
        os.mkdir(pai_env_path)
        for cur_dir in PAI_FILESTRUCTURE['directories'].values():
            os.makedirs(f"{pai_env_path}/{cur_dir}", exist_ok=True)

    @staticmethod
    def load_setting(pai_base_path: str, pai_name: str) \
        -> Tuple[BaseComponentConfig, Union[None, KeyValueDriverConfig], 
                 Union[None, AgentStatAnalyzerConfig]]:
        if (type(pai_base_path) is not str) or (type(pai_name) is not str):
            raise TypeError

        pai_env_path = f"{pai_base_path}/{pai_name}"
        is_env_exists = os.path.exists(pai_env_path)
        if not is_env_exists:
            raise ValueError(f"Specified PersonalAI environment '{pai_env_path}' is not exists.")

        pai_setting_dir = f"{pai_env_path}/{PAI_FILESTRUCTURE['directories']['setting']}"

        pai_partial_path = f"{pai_setting_dir}/{PAI_FILESTRUCTURE['configuration_files']['required']['personalai_partial_config']}"
        with open(pai_partial_path, "r") as fd:
            pai_partial_config: Dict = yaml.safe_load(fd)

        # loading PersonalAIConfig
        pai_config_parts = dict()
        for pai_part_name in ['kg_model_config', 'textidstore_config', 'mem_pipeline_config']:
            config_path = f"{pai_setting_dir}/{PAI_FILESTRUCTURE['configuration_files']['required'][pai_part_name]}"
            pai_config_parts[pai_part_name] = KW_TO_CONFIGURATIONS_MAPPING[pai_part_name].load(config_path)
        qa_pipeline_path = f"{pai_setting_dir}/{PAI_FILESTRUCTURE['configuration_files']['optional']['qa_pipeline_config']}"
        if os.path.exists(qa_pipeline_path):
            pai_config_parts['qa_pipeline_config'] = KW_TO_CONFIGURATIONS_MAPPING['qa_pipeline_config'].load(qa_pipeline_path)
        pai_config = PersonalAIConfig(**pai_partial_config, **pai_config_parts)

        # loading KeyValueDriverConfig
        cache_kvdriver_config = None
        cache_kvdriver_path = f"{pai_setting_dir}/{PAI_FILESTRUCTURE['configuration_files']['optional']['cache_kvdriver_config']}"
        if os.path.exists(cache_kvdriver_path):
            cache_kvdriver_config = KW_TO_CONFIGURATIONS_MAPPING['cache_kvdriver_config'].load(cache_kvdriver_path)

        # loading AgentStatAnalyzerConfig
        inferencestat_config = None
        inferencestat_path = f"{pai_setting_dir}/{PAI_FILESTRUCTURE['configuration_files']['optional']['inferencestat_config']}"
        if os.path.exists(inferencestat_path):
            inferencestat_config = KW_TO_CONFIGURATIONS_MAPPING['inferencestat_config'].load(inferencestat_path)

        return pai_config, cache_kvdriver_config, inferencestat_config

    @staticmethod
    def prepare_setting(config: PersonalAIConfig, cache_kvdriver_config: Union[None, KeyValueDriverConfig], 
            inferencestat_config: Union[None, AgentStatAnalyzerConfig]):
        if type(config) is not PersonalAIConfig:
            raise TypeError
        if (cache_kvdriver_config is not None) and \
            (type(cache_kvdriver_config) is not KeyValueDriverConfig):
            raise TypeError
        if (inferencestat_config is not None) and \
            (type(inferencestat_config) is not AgentStatAnalyzerConfig):
            raise TypeError
                
        # priority to configs, what is stored in existing pai-environmnet
        
        env_config, env_cache_kvdriver_config, env_inferencestat_config = \
            EnvironmentUtils.load_setting(config.pai_base_path, config.pai_name)

        pai_env_path = f"{config.pai_base_path}/{config.pai_name}"
        pai_setting_dir = f"{pai_env_path}/{PAI_FILESTRUCTURE['directories']['setting']}"        
        
        qa_pipeline_path = f"{pai_setting_dir}/{PAI_FILESTRUCTURE['configuration_files']['optional']['qa_pipeline_config']}"
        if not os.path.exists(qa_pipeline_path):
           env_config.qa_pipeline_config = deepcopy(config.qa_pipeline_config)
        selected_pai_config = env_config

        if env_cache_kvdriver_config is not None:
            selected_cache_kvdriver_config = None if cache_kvdriver_config is None else env_cache_kvdriver_config
        else:
            selected_cache_kvdriver_config = deepcopy(cache_kvdriver_config)

        if env_inferencestat_config is not None:
            selected_inferencestat_config = None if inferencestat_config is None else env_inferencestat_config
        else:
            selected_inferencestat_config = deepcopy(inferencestat_config)

        return selected_pai_config, selected_cache_kvdriver_config, selected_inferencestat_config

    @staticmethod
    def save_setting(config: PersonalAIConfig, cache_kvdriver_config: Union[None, KeyValueDriverConfig], 
            inferencestat_config: Union[None, AgentStatAnalyzerConfig]) -> None:
        if type(config) is not PersonalAIConfig:
            raise TypeError
        if (cache_kvdriver_config is not None) and \
            (type(cache_kvdriver_config) is not KeyValueDriverConfig):
            raise TypeError
        if (inferencestat_config is not None) and \
            (type(inferencestat_config) is not AgentStatAnalyzerConfig):
            raise TypeError

        pai_setting_dir = f"{config.pai_base_path}/{config.pai_name}/{PAI_FILESTRUCTURE['directories']['setting']}"
        
        if cache_kvdriver_config is not None:
            kvcache_save_path = f"{pai_setting_dir}/{PAI_FILESTRUCTURE['configuration_files']['optional']['cache_kvdriver_config']}"
            cache_kvdriver_config.save(kvcache_save_path)
        if inferencestat_config is not None:
            inferencestat_save_path = f"{pai_setting_dir}/{PAI_FILESTRUCTURE['configuration_files']['optional']['inferencestat_config']}"
            inferencestat_config.save(inferencestat_save_path)

        qapipeline_save_path = f"{pai_setting_dir}/{PAI_FILESTRUCTURE['configuration_files']['optional']['qa_pipeline_config']}"
        config.qa_pipeline_config.save(qapipeline_save_path)
        mempipeline_save_path = f"{pai_setting_dir}/{PAI_FILESTRUCTURE['configuration_files']['required']['mem_pipeline_config']}"
        config.mem_pipeline_config.save(mempipeline_save_path)
        kgmodel_save_path = f"{pai_setting_dir}/{PAI_FILESTRUCTURE['configuration_files']['required']['kg_model_config']}"
        config.kg_model_config.save(kgmodel_save_path)
        textidstore_save_path = f"{pai_setting_dir}/{PAI_FILESTRUCTURE['configuration_files']['required']['textidstore_config']}"
        config.textidstore_config.save(textidstore_save_path)

        paipartial_save_path = f"{pai_setting_dir}/{PAI_FILESTRUCTURE['configuration_files']['required']['personalai_partial_config']}"     
        pai_dict_config: Dict = asdict(config, dict_factory=config.custom_formatter)
        del pai_dict_config['textidstore_config']
        del pai_dict_config['kg_model_config']
        del pai_dict_config['mem_pipeline_config']
        del pai_dict_config['qa_pipeline_config']
        with open(paipartial_save_path, "w") as fd:
            yaml.dump(pai_dict_config, fd, default_flow_style=False, sort_keys=False, allow_unicode=True)
        
