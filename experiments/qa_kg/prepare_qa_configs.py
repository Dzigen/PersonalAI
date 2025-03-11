# генерируем kg_reasoner конфиг на основании params.yaml файла

import sys
import os
import yaml
import json
import joblib
import copy

# Read YAML file
PARAMS_FILEP = sys.orig_argv[2]
with open(PARAMS_FILEP, 'r') as stream:
    PARAMS = yaml.safe_load(stream)

sys.path.insert(0, PARAMS['BASE_PERSONALAI_DIR'])

from src.pipelines.qa.kg_reasoning.weak_reasoner import WeakKGReasonerConfig
from src.pipelines.qa.kg_reasoning.weak_reasoner import QueryLLMParserConfig, KnowledgeComparatorConfig, \
    KnowledgeRetrieverConfig, QALLMGeneratorConfig

from src.pipelines.qa.kg_reasoning.weak_reasoner.query_parser.agent_tasks.kw_extraction import AgentKWETaskConfigSelector
from src.pipelines.qa.kg_reasoning.weak_reasoner.answer_generator.agent_tasks.ag import AgentAGTaskConfigSelector

from src.agents import AgentDriverConfig
from src.agents.utils import AgentConnectorConfig

################ hyperparams #####################

KG_DIR_PATH = f"{PARAMS['KGS_BASE_PATH']}/{PARAMS['DATASET_NAME']}/{PARAMS['KNOWLEDGE_GRAPH_NAME']}"
MEM_PARAMS_FILEP = f"{KG_DIR_PATH}/{PARAMS['MEM_PIPELINE_HYPERP']}"
with open(MEM_PARAMS_FILEP, 'r') as stream:
    MEM_PARAMS = yaml.safe_load(stream)

DS_EXPERIMENT_DIR = f"{PARAMS['EXPERIMENTS_BASE_DIR']}/{PARAMS['DATASET_NAME']}"
SPEC_EXPERIMENT_DIR = f"{DS_EXPERIMENT_DIR}/{PARAMS['EXPERIMENT_NAME']}"
KG_REASONSER_CONFIG_SPATH = f"{SPEC_EXPERIMENT_DIR}/{PARAMS['SAVE_FILES_NAMES']['kg_reasoner_config']}"

################ agent driver config #####################

adriver_config = AgentDriverConfig(
    name=PARAMS['BASE_KGR_CONFIG']['agent_config']['vendor'],
    agent_config=AgentConnectorConfig(
        gen_strategy=PARAMS['BASE_KGR_CONFIG']['agent_config']['gen_strategy'],
        credentials=PARAMS['BASE_KGR_CONFIG']['agent_config']['credentials'],
        ext_params=PARAMS['BASE_KGR_CONFIG']['agent_config']['ext_params']))

################ KG REAONER ################

if PARAMS['BASE_KGR_CONFIG']['name'] == 'weak':

    k_retriever_config = KnowledgeRetrieverConfig(
        retriever_method=PARAMS['WEAK_KG_REASONER']['knowledge_retriever_config']['retriever_method'],
        retriever_config=PARAMS['WEAK_KG_REASONER']['knowledge_retriever_config']['retriever_config'],
        filter_method=PARAMS['WEAK_KG_REASONER']['knowledge_retriever_config']['filter_method'],
        filter_config=PARAMS['WEAK_KG_REASONER']['knowledge_retriever_config']['filter_method'])

    kg_reasoner_config = WeakKGReasonerConfig(
        query_parser_config=QueryLLMParserConfig(
            lang=PARAMS['BASE_KGR_CONFIG']['lang'],
            adriver_config=adriver_config,
            kw_extraction_task_config=AgentKWETaskConfigSelector.select(
                base_config_version=PARAMS['WEAK_KG_REASONER']['query_parser_config']['kw_extraction_task']['prompts_version'])),
        knowledge_comparator_config=KnowledgeComparatorConfig(
            **PARAMS['WEAK_KG_REASONER']['knowledge_comparator_config']),
        knowledge_retriever_config=k_retriever_config,
        answer_generator_config=QALLMGeneratorConfig(
            lang=PARAMS['BASE_KGR_CONFIG']['lang'],
            adriver_config=adriver_config,
            ag_task_config=AgentAGTaskConfigSelector.select(
                base_config_version=PARAMS['WEAK_KG_REASONER']['answer_generator_config']['ag_task']['prompts_version'])))
else:
    raise ValueError

# вывести полученный конфиг в stdout
print("Полученная kg_reasoner-конфигурация:")
print(kg_reasoner_config)

# сохранить полученный конфиг в директорию соответствующего эксперимента
with open(KG_REASONSER_CONFIG_SPATH, 'wb') as fd:
    joblib.dump(kg_reasoner_config, fd)
