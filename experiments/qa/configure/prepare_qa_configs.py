print("Start QA-config generation...")
import sys
import yaml
import joblib
from copy import deepcopy
from pprint import pprint

####################################################
print("1. Loading hyperparameters from .yaml files")

# Read YAML file (specexp-params)
SPECEXP_PARAMS_FILEP = sys.orig_argv[2]
with open(SPECEXP_PARAMS_FILEP, 'r') as stream:
    SPECEXP_PARAMS = yaml.safe_load(stream)

# Read YAML file (expdir-params)
EXPDIR_PARAMS_FILEP = sys.orig_argv[3]
with open(EXPDIR_PARAMS_FILEP, 'r') as stream:
    EXPDIR_PARAMS = yaml.safe_load(stream)

sys.path.insert(0, EXPDIR_PARAMS['WORKSPACE_CONTAINER_DIRS']['base_path'])

from src.pipelines.qa.query_preprocessing import QueryPreprocessorConfig
from src.pipelines.qa.kg_reasoning import KnowledgeGraphReasonerConfig
from src.pipelines.qa.answers_aggregation import AnswersAggregatorConfig

from src.pipelines.qa import QAPipelineConfig

####################################################
print("2. Setting paths")

EXP_RESULTS_DIR = f"{EXPDIR_PARAMS['WORKSPACE_CONTAINER_DIRS']['base_path']}/{EXPDIR_PARAMS['WORKSPACE_CONTAINER_DIRS']['experiments']}/{EXPDIR_PARAMS['WORKSPACE_CONTAINER_DIRS']['results']}"
EXP_KG_PATH = f"{EXP_RESULTS_DIR}/{SPECEXP_PARAMS['DATASET_NAME']}/{SPECEXP_PARAMS['KNOWLEDGE_GRAPH_NAME']}"
SPEC_EXPERIMENT_DIR = f"{EXP_KG_PATH}/{SPECEXP_PARAMS['EXPERIMENT_NAME']}"

CONFIGS_PATH = f"{SPEC_EXPERIMENT_DIR}/{EXPDIR_PARAMS['EXP_DIRS']['configs_name']}"
QPREPROC_CONFIG_SPATH = f"{CONFIGS_PATH}/{EXPDIR_PARAMS['EXP_SAVE_FILES']['qpreproc_config']}"
KG_REASONSER_CONFIG_SPATH = f"{CONFIGS_PATH}/{EXPDIR_PARAMS['EXP_SAVE_FILES']['kgreasoner_config']}"
ANSWAGGR_CONFIG_SPATH = f"{CONFIGS_PATH}/{EXPDIR_PARAMS['EXP_SAVE_FILES']['aaggregator_config']}"
QA_CONFIG_SPATH = f"{CONFIGS_PATH}/{EXPDIR_PARAMS['EXP_SAVE_FILES']['qa_config']}"

SETTINGS_PATH = f"{SPEC_EXPERIMENT_DIR}/{EXPDIR_PARAMS['EXP_DIRS']['settings_name']}"
EXPDIR_PARAMS_SPATH = f"{SETTINGS_PATH}/{EXPDIR_PARAMS['EXP_SAVE_FILES']['expdir']}"
SPECEXP_PARAMS_SPATH = f"{SETTINGS_PATH}/{EXPDIR_PARAMS['EXP_SAVE_FILES']['qahyperp']}"

####################################################
print("3. Configuring Query Preprocessor stage")

qprep_config = deepcopy(SPECEXP_PARAMS['query_preprocessor'])
querypreproc_config = QueryPreprocessorConfig(**qprep_config)
querypreproc_config.formate_fields()

####################################################
print("4. Configuring Answer Aggregation stage")

answagg_config = deepcopy(SPECEXP_PARAMS['answer_aggregator'])
answeraggr_config = AnswersAggregatorConfig(**answagg_config)
answeraggr_config.formate_fields()

####################################################
print("5. Configuring KG Reasoner stage")

kgreason_config = deepcopy(SPECEXP_PARAMS['kg_reasoner'])
kg_reasoner_config = KnowledgeGraphReasonerConfig(**kgreason_config)
kg_reasoner_config.formate_fields()

####################################################
print("6. Composing QA-config")

qa_config = QAPipelineConfig(
    lang=SPECEXP_PARAMS['QA_DATASET_HYPERP']['lang'],
    preprocessor_config=querypreproc_config,
    reasoner_config=kg_reasoner_config,
    aggregator_config=answeraggr_config
)
qa_config.formate_fields()
qa_config.synchronize_language()

####################################################
print("7. Saving configs")

print("Полученная query_preproc-конфигурация:")
print(querypreproc_config)
print("Полученная kg_reasoner-конфигурация:")
print(kg_reasoner_config)
print("Полученная answers_aggr-конфигурация:")
print(answeraggr_config)
print("Полученная qa-конфигурация:")
print(qa_config)

with open(QPREPROC_CONFIG_SPATH, 'wb') as fd:
    joblib.dump(querypreproc_config, fd)
with open(KG_REASONSER_CONFIG_SPATH, 'wb') as fd:
    joblib.dump(kg_reasoner_config, fd)
with open(ANSWAGGR_CONFIG_SPATH, 'wb') as fd:
    joblib.dump(answeraggr_config, fd)
with open(QA_CONFIG_SPATH, 'wb') as fd:
    joblib.dump(qa_config, fd)

with open(SPECEXP_PARAMS_SPATH, 'w') as fd:
    yaml.dump(SPECEXP_PARAMS, fd, default_flow_style=False)
with open(EXPDIR_PARAMS_SPATH, 'w') as fd:
    yaml.dump(EXPDIR_PARAMS, fd, default_flow_style=False)

print("############ DONE ############")
