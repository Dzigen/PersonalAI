from typing import Dict,  Union
from dataclasses import dataclass, field
from copy import deepcopy

from .kg_model import  KnowledgeGraphModelConfig
from .pipelines.qa import QAPipelineConfig
from .pipelines.memorize import  MemPipelineConfig
from .utils.data_structs import BaseComponentConfig, LanguageConfig, EnvironmentConfig
from .db_drivers.kv_driver import KeyValueDriverConfig
from .config import PAI_MAIN_LOG_PATH
from .utils.agent_stat_analyzer import AgentStatAnalyzerConfig
from .TextIdStore import TextIdStoreConfig
from .environment.config import PAI_FILESTRUCTURE

@dataclass
class PersonalAIConfig(BaseComponentConfig, LanguageConfig, EnvironmentConfig):
    """Конфигурация персонального ассистента.

    :param kg_model_config: Конфигурация памяти ассистента. Значение по умолчанию KnowledgeGraphModelConfig().
    :type kg_model_config: Union[KnowledgeGraphModelConfig, Dict], optional
    :param qa_pipeline_config: Конфигурация конвейера, который выполняет обработку входящих user-вопросов, поиск релевантной информации в памяти ассистента и генерацию ответов. Значение по умолчанию QAPipelineConfig().
    :type qa_pipeline_config: Union[QAPipelineConfig, Dict], optional
    :param mem_pipeline_config: Конфигурация конвейера, который выполняет изменение/обновление информации/знаний в памяти ассистента. Значение по умолчанию MemPipelineConfig().
    :type mem_pipeline_config: Union[MemPipelineConfig, Dict], optional
    :param textidstore_config: Конфигурация хранилища отображений между исходными текстами (сохранёнными в модель памяти) и извлечёнными (из данных текстов) триплетами. Значение по умолчанию TextIdStoreConfig().
    :type textidstore_config: Union[TextIdStoreConfig, Dict], optional
    """
    kg_model_config: Union[KnowledgeGraphModelConfig, Dict] = field(default_factory=lambda: KnowledgeGraphModelConfig())
    qa_pipeline_config: Union[QAPipelineConfig, Dict] = field(default_factory=lambda: QAPipelineConfig())
    mem_pipeline_config: Union[MemPipelineConfig, Dict] = field(default_factory=lambda: MemPipelineConfig())
    textidstore_config: Union[TextIdStoreConfig, Dict] = field(default_factory=lambda: TextIdStoreConfig())

    load_existing_environment: bool = True

    log_base_path: Union[None, str] = None
    log_relative_path: str = PAI_MAIN_LOG_PATH

    def to_str(self):
        # TODO
        raise NotImplementedError

    @staticmethod
    def from_dict(dict_config: Dict):
        dictconfig_copy = deepcopy(dict_config)
        formated_config = PersonalAIConfig(**dictconfig_copy)
        formated_config.formate_fields()
        return formated_config

    def formate_fields(self):
        if isinstance(self.kg_model_config, dict):
            self.kg_model_config = KnowledgeGraphModelConfig.from_dict(self.kg_model_config)
        else:
            self.kg_model_config.formate_fields()

        if isinstance(self.qa_pipeline_config, dict):
            self.qa_pipeline_config = QAPipelineConfig.from_dict(self.qa_pipeline_config)
        else:
            self.qa_pipeline_config.formate_fields()

        if isinstance(self.mem_pipeline_config, dict):
            self.mem_pipeline_config = MemPipelineConfig.from_dict(self.mem_pipeline_config)
        else:
            self.mem_pipeline_config.formate_fields()

        if isinstance(self.textidstore_config, dict):
            self.textidstore_config = TextIdStoreConfig.from_dict(self.textidstore_config)
        else:
            self.textidstore_config.formate_fields()

    def synchronize_cache_kvdriver_config(self, cache_kvdriver_config: KeyValueDriverConfig) -> None:
        if type(cache_kvdriver_config) is not KeyValueDriverConfig:
            raise TypeError
        cache_path = f"{self.pai_base_path}/{self.pai_name}/{PAI_FILESTRUCTURE['directories']['cache']}"
        cache_kvdriver_config.db_config.update_db_location(db_path=cache_path, db_name=self.kg_related_database_name)

    def synchronize_inferencestat_config(self, inferencestat_config: AgentStatAnalyzerConfig) -> None:
        if type(inferencestat_config) is not AgentStatAnalyzerConfig:
            raise TypeError
        agentstat_path = f"{self.pai_base_path}/{self.pai_name}/{PAI_FILESTRUCTURE['directories']['agent_stat']}"
        inferencestat_config.table_driver_config.db_config.update_db_location(db_path=agentstat_path, db_name=self.kg_related_database_name)
