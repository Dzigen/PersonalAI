print("Creating MemPipeline config file...")
import sys
import joblib
import yaml

####################################################
print("1. Loading hyperparameters from .yaml files")

# Read YAML file (kg-env)
KGENV_FILE_PATH = sys.orig_argv[2]
with open(KGENV_FILE_PATH, 'r') as stream:
    KGENV_PARAMS = yaml.safe_load(stream)

# Read YAML file (kg-hyperp)
KGHYPERP_FILE_PATH = sys.orig_argv[3]
with open(KGHYPERP_FILE_PATH, 'r') as stream:
    KGHYPERP_PARAMS = yaml.safe_load(stream)

sys.path.insert(0, KGENV_PARAMS['WORKSPACE_CONTAINER_DIRS']['base_path'])

from src.pipelines.memorize import MemPipelineConfig, LLMExtractorConfig, LLMUpdatorConfig
from src.pipelines.memorize.extractor.configs import AgentThesisExtrTaskConfigSelector, AgentTripletExtrTaskConfigSelector

####################################################
print("2. Setting paths")

DATASET_KGS_PATH = f"{KGENV_PARAMS['WORKSPACE_CONTAINER_DIRS']['base_path']}/{KGENV_PARAMS['WORKSPACE_CONTAINER_DIRS']['kg']}/{KGHYPERP_PARAMS['DATASET_NAME']}"
SPEC_KG_PATH = f"{DATASET_KGS_PATH}/{KGHYPERP_PARAMS['KNOWLEDGE_GRAPH_NAME']}"

MEM_PIPELINE_CONFIG_PATH = f"{SPEC_KG_PATH}/{KGENV_PARAMS['SAVE_CONFIGS_NAMES']['mem_pipeline_config']}"

####################################################
print("3. Setting MemPipeline Config")

MEMPIPE_CONFIG = KGHYPERP_PARAMS['MEM_PIPELINE_CONFIG']

# extractor stage config
extractor_config = LLMExtractorConfig(
    lang=MEMPIPE_CONFIG['lang'],
    triplets_extraction_task_config=AgentTripletExtrTaskConfigSelector.select(
        base_config_version=MEMPIPE_CONFIG['extractor_stage']['extract_triplets']['prompts_version']),
    thesises_extraction_task_config=AgentThesisExtrTaskConfigSelector.select(
        base_config_version=MEMPIPE_CONFIG['extractor_stage']['extract_thesises']['prompts_version']),
)

# Setting Memorization Pipeline
mem_config = MemPipelineConfig(
    extractor_config=extractor_config,
    updator_config=LLMUpdatorConfig(
        lang=MEMPIPE_CONFIG['lang'],
        delete_obsolete_info=False
    ))

####################################################
print("4. Saving MemPipeline Config")

print("mem: ", mem_config)
joblib.dump(mem_config, MEM_PIPELINE_CONFIG_PATH)
