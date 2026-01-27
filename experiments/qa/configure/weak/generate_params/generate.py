import sys
import os
import yaml
from copy import deepcopy
from itertools import product
import hashlib

#############################################################

SETTINGS_PARAMS_FILEP = sys.orig_argv[2]
with open(SETTINGS_PARAMS_FILEP, 'r') as stream:
    SETTINGS_PARAMS = yaml.safe_load(stream)

#############################################################

REPO_BASE_PATH = '/home/m.menschikov/workspace/personal_ai/Personal-AI' #'/home/workspace' # TO CHANGE
GEN_PARAMS_PATH = f'{REPO_BASE_PATH}/experiments/qa/configure/weak/generate_params'
SAVE_PARAMS_PATH = f'{GEN_PARAMS_PATH}/tmp_params'

#############################################################

QPREP_CONFIGS = SETTINGS_PARAMS['query_preprocessor']
AVAIL_QDEN_CONFIGS = QPREP_CONFIGS['denoising_config']
AVAIL_QENH_CONFIGS = QPREP_CONFIGS['enhancing_config']
AVAIL_QDEC_CONFIGS = QPREP_CONFIGS['decomposition_config']

KGREAS_CONFIGS = SETTINGS_PARAMS['kg_reasoner']['reasoner_config']
AVAIL_QPARS_CONFIGS = KGREAS_CONFIGS['query_parser_config']
AVAIL_KCOMP_CONFIGS = KGREAS_CONFIGS['knowledge_comparator_config']

KRETR_CONFIGS = KGREAS_CONFIGS['knowledge_retriever_config']
AVAIL_KRETR_CONFIGS = [(ret_method, ret_config) for ret_method, ret_config in zip(KRETR_CONFIGS['retriever_method'], KRETR_CONFIGS['retriever_config'])]
AVAIL_KFILTR_CONFIGS = [(filt_method, filt_config) for filt_method, filt_config in zip(KRETR_CONFIGS['filter_method'], KRETR_CONFIGS['filter_config'])]

AVAIL_ANSWGEN_CONFIGS = KGREAS_CONFIGS['answer_generator_config']

AVAIL_ANSWAGG_PVERSIONS = SETTINGS_PARAMS['answer_aggregator']['agent_tasks_config']['suba_summarisation']

GENERAL_QAPIPE_CONFIGS = list(product(
    AVAIL_QDEN_CONFIGS, # 0
    AVAIL_QENH_CONFIGS, # 1
    AVAIL_QDEC_CONFIGS, # 2
    AVAIL_QPARS_CONFIGS, # 3
    AVAIL_KCOMP_CONFIGS, # 4
    AVAIL_KRETR_CONFIGS, # 5
    AVAIL_KFILTR_CONFIGS, # 6
    AVAIL_ANSWGEN_CONFIGS, # 7
    AVAIL_ANSWAGG_PVERSIONS # 8
))

#############################################################

AVAILABLE_DATASET_NAMES = SETTINGS_PARAMS['DATASET_NAME']
for ds_idx, dataset in enumerate(AVAILABLE_DATASET_NAMES):
    SPEC_DATASET_PATH = f"{SAVE_PARAMS_PATH}/{dataset}"
    if not os.path.exists(SPEC_DATASET_PATH):
        os.mkdir(SPEC_DATASET_PATH)

    AVAILABLE_KG_NAMES = SETTINGS_PARAMS['KNOWLEDGE_GRAPH_NAME'][ds_idx]
    for kg_idx, kg_name in enumerate(AVAILABLE_KG_NAMES):
        SPEC_KG_PATH = f"{SPEC_DATASET_PATH}/{kg_name}"
        if not os.path.exists(SPEC_KG_PATH):
            os.mkdir(SPEC_KG_PATH)

        CURENT_LANG = SETTINGS_PARAMS['QA_DATASET_HYPERP']['lang'][ds_idx]

        for spec_raw_params in GENERAL_QAPIPE_CONFIGS:
            SPECIFIC_QA_PARAMS = deepcopy(SETTINGS_PARAMS)

            # setting specific values for available hyperparameters
            SPECIFIC_QA_PARAMS['DATASET_NAME'] = dataset
            SPECIFIC_QA_PARAMS['KNOWLEDGE_GRAPH_NAME'] = kg_name
            SPECIFIC_QA_PARAMS['QA_DATASET_HYPERP']['lang'] = CURENT_LANG

            SPECIFIC_QA_PARAMS['query_preprocessor']['denoising_config'] = deepcopy(spec_raw_params[0])
            SPECIFIC_QA_PARAMS['query_preprocessor']['enhancing_config'] = spec_raw_params[1]
            SPECIFIC_QA_PARAMS['query_preprocessor']['decomposition_config'] = spec_raw_params[2]
            
            SPECIFIC_QA_PARAMS['kg_reasoner']['reasoner_config']['query_parser_config'] = spec_raw_params[3]
            SPECIFIC_QA_PARAMS['kg_reasoner']['reasoner_config']['knowledge_comparator_config'] = spec_raw_params[4]
            
            SPECIFIC_QA_PARAMS['kg_reasoner']['reasoner_config']['knowledge_retriever_config']['retriever_method'] = spec_raw_params[5][0]
            SPECIFIC_QA_PARAMS['kg_reasoner']['reasoner_config']['knowledge_retriever_config']['retriever_config'] = spec_raw_params[5][1]
            
            SPECIFIC_QA_PARAMS['kg_reasoner']['reasoner_config']['knowledge_retriever_config']['filter_method'] = spec_raw_params[6][0]
            SPECIFIC_QA_PARAMS['kg_reasoner']['reasoner_config']['knowledge_retriever_config']['filter_config'] = spec_raw_params[6][1]
            
            SPECIFIC_QA_PARAMS['kg_reasoner']['reasoner_config']['answer_generator_config'] = spec_raw_params[7]
            
            SPECIFIC_QA_PARAMS['answer_aggregator']['agent_tasks_config']['suba_summarisation'] = spec_raw_params[8]

            # creating name for experiment
            short_ds_name = dataset.split('_')[0]
            short_kg_name = kg_name.split('_')[0]
            reasoner_kw = SETTINGS_PARAMS['kg_reasoner']['reasoner_name']
            retrmethod_name = ''.join(SPECIFIC_QA_PARAMS['kg_reasoner']['reasoner_config']['knowledge_retriever_config']['retriever_method'].split("_"))
            exp_id = hashlib.md5(str(SPECIFIC_QA_PARAMS).encode()).hexdigest()[:8]
            SPECIFIC_QA_PARAMS['EXPERIMENT_NAME'] = f"{short_ds_name}_{short_kg_name}_{reasoner_kw}_{retrmethod_name}(#{exp_id})({SETTINGS_PARAMS['PERSONALAI_VERSION']})"

            # saving generated params-config
            SPEC_PARAMS_SPATH = f"{SAVE_PARAMS_PATH}/{dataset}/{kg_name}/{SPECIFIC_QA_PARAMS['EXPERIMENT_NAME']}.yaml"
            if os.path.exists(SPEC_PARAMS_SPATH):
                print(f"params-file already exists: {SPEC_PARAMS_SPATH}")
                continue

            with open(SPEC_PARAMS_SPATH, 'w') as fd:
                yaml.dump(
                    SPECIFIC_QA_PARAMS, fd, 
                    default_flow_style=False, 
                    sort_keys=False
                )

print("############ DONE ############")