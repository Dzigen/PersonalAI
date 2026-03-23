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

REPO_BASE_PATH = '/home/m.menschikov/workspace/personal_ai/Personal-AI' #'/home/workspace' | '/home/m.menschikov/workspace/personal_ai/Personal-AI' # TO CHANGE
GEN_PARAMS_PATH = f'{REPO_BASE_PATH}/experiments/qa/configure/medium/generate_params'
SAVE_PARAMS_PATH = f'{GEN_PARAMS_PATH}/tmp_params'

#############################################################

QPREP_CONFIGS = SETTINGS_PARAMS['query_preprocessor']
AVAIL_QDEN_CONFIGS = QPREP_CONFIGS['denoising_config']
AVAIL_QENH_CONFIGS = QPREP_CONFIGS['enhancing_config']
AVAIL_QDEC_CONFIGS = QPREP_CONFIGS['decomposition_config']

KGREAS_CONFIGS = SETTINGS_PARAMS['kg_reasoner']['reasoner_config']

AVAIL_SSTEPS = KGREAS_CONFIGS['max_searchplan_steps']
AVAIL_ANSWSOME = KGREAS_CONFIGS['answer_something']

AVAIL_SEARCHENCH_CONFIGS = KGREAS_CONFIGS['searchplan_enhancer_config']

AVAIL_ENTEXTR_CONFIGS = KGREAS_CONFIGS['entities_extractor_config']
AVAIL_E2NMATCHER_CONFIGS = KGREAS_CONFIGS['e2n_matcher_config']

AVAIL_CQUERIES = KGREAS_CONFIGS['cluequeries_generator_config']['max_cqueries_amount']
AVAIL_CQUERIESGEN_PVERSIONS = KGREAS_CONFIGS['cluequeries_generator_config']['agent_tasks_config']['cquerie_generator']

KRETR_CONFIGS = KGREAS_CONFIGS['knowledge_retriever_config']
AVAIL_KRETR_CONFIGS = [(ret_method, ret_config) for ret_method, ret_config in zip(KRETR_CONFIGS['retriever_method'], KRETR_CONFIGS['retriever_config'])]
AVAIL_KFILTR_CONFIGS = [(filt_method, filt_config) for filt_method, filt_config in zip(KRETR_CONFIGS['filter_method'], KRETR_CONFIGS['filter_config'])]

AVAIL_CANSWGEN_PVERSIONS = KGREAS_CONFIGS['clueanswer_generator_config']['agent_tasks_config']['cagen']
AVAIL_CANSWSUM_PVERSIONS = KGREAS_CONFIGS['clueanswers_summarizer_config']['agent_tasks_config']['canswers_summarisation']

ANSWGEN_CONFIGS = KGREAS_CONFIGS['answer_generator_config']
AVAIL_ANSWCLS_PVERSIONS = ANSWGEN_CONFIGS['agent_tasks_config']['answer_classifier']
AVAIL_ANSWGEN_PVERSIONS = ANSWGEN_CONFIGS['agent_tasks_config']['answer_generator']

AVAIL_ANSWAGG_PVERSIONS = SETTINGS_PARAMS['answer_aggregator']['agent_tasks_config']['suba_summarisation']

GENERAL_QAPIPE_CONFIGS = list(product(
    AVAIL_QDEN_CONFIGS, # 0
    AVAIL_QENH_CONFIGS, # 1
    AVAIL_QDEC_CONFIGS, # 2

    AVAIL_SSTEPS, # 3
    AVAIL_ANSWSOME, # 4
    
    AVAIL_SEARCHENCH_CONFIGS, # 5
    AVAIL_ENTEXTR_CONFIGS, # 6
    AVAIL_E2NMATCHER_CONFIGS, # 7
    
    AVAIL_CQUERIES, # 8
    AVAIL_CQUERIESGEN_PVERSIONS, # 9
    
    AVAIL_KRETR_CONFIGS, # 10
    AVAIL_KFILTR_CONFIGS, # 11
    
    AVAIL_CANSWGEN_PVERSIONS, # 12
    
    AVAIL_CANSWSUM_PVERSIONS, # 13

    AVAIL_ANSWCLS_PVERSIONS, # 14
    AVAIL_ANSWGEN_PVERSIONS, # 15
    
    AVAIL_ANSWAGG_PVERSIONS # 16
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
            
            SPECIFIC_QA_PARAMS['kg_reasoner']['reasoner_config']['max_searchplan_steps'] = spec_raw_params[3]
            SPECIFIC_QA_PARAMS['kg_reasoner']['reasoner_config']['answer_something'] = spec_raw_params[4]

            SPECIFIC_QA_PARAMS['kg_reasoner']['reasoner_config']['searchplan_enhancer_config'] = spec_raw_params[5]
            SPECIFIC_QA_PARAMS['kg_reasoner']['reasoner_config']['entities_extractor_config'] = spec_raw_params[6]
            SPECIFIC_QA_PARAMS['kg_reasoner']['reasoner_config']['e2n_matcher_config'] = spec_raw_params[7]

            SPECIFIC_QA_PARAMS['kg_reasoner']['reasoner_config']['cluequeries_generator_config']['max_cqueries_amount'] = spec_raw_params[8]
            SPECIFIC_QA_PARAMS['kg_reasoner']['reasoner_config']['cluequeries_generator_config']['agent_tasks_config']['cquerie_generator'] = spec_raw_params[9]

            SPECIFIC_QA_PARAMS['kg_reasoner']['reasoner_config']['knowledge_retriever_config']['retriever_method'] = spec_raw_params[10][0]
            SPECIFIC_QA_PARAMS['kg_reasoner']['reasoner_config']['knowledge_retriever_config']['retriever_config'] = spec_raw_params[10][1]
            
            SPECIFIC_QA_PARAMS['kg_reasoner']['reasoner_config']['knowledge_retriever_config']['filter_method'] = spec_raw_params[11][0]
            SPECIFIC_QA_PARAMS['kg_reasoner']['reasoner_config']['knowledge_retriever_config']['filter_config'] = spec_raw_params[11][1]

            SPECIFIC_QA_PARAMS['kg_reasoner']['reasoner_config']['clueanswer_generator_config']['agent_tasks_config']['cagen'] = spec_raw_params[12]

            SPECIFIC_QA_PARAMS['kg_reasoner']['reasoner_config']['clueanswers_summarizer_config']['agent_tasks_config']['canswers_summarisation'] = spec_raw_params[13]

            SPECIFIC_QA_PARAMS['kg_reasoner']['reasoner_config']['answer_generator_config']['agent_tasks_config']['answer_classifier'] = spec_raw_params[14]
            SPECIFIC_QA_PARAMS['kg_reasoner']['reasoner_config']['answer_generator_config']['agent_tasks_config']['answer_generator'] = spec_raw_params[15]

            SPECIFIC_QA_PARAMS['answer_aggregator']['agent_tasks_config']['suba_summarisation'] = spec_raw_params[16]

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