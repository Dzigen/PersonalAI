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

REPO_BASE_PATH = '/home/m.menschikov/workspace/personal_ai/Personal-AI' #'/home/m.menschikov/workspace/personal_ai/Personal-AI' | '/home/workspace' # TO CHANGE
GEN_PARAMS_PATH = f'{REPO_BASE_PATH}/experiments/kg_eval/mine/configure/generate_params'
SAVE_PARAMS_PATH = f'{GEN_PARAMS_PATH}/tmp_params'

#############################################################

AVAIL_MAXMNODES = SETTINGS_PARAMS['RETRIEVE_SETTING']['max_matched_nodes']
AVAIL_MAXTRIPLES_PERQUERY = SETTINGS_PARAMS['RETRIEVE_SETTING']['max_triples_per_node']
AVAIL_MAXNODE_PERDEPTH = SETTINGS_PARAMS['RETRIEVE_SETTING']['max_nodes_per_depth']
AVAIL_MAXEXPLORE_DEPTH = SETTINGS_PARAMS['RETRIEVE_SETTING']['max_explore_depth']
AVAIL_MAXTRIPLES_INTOTAL = SETTINGS_PARAMS['RETRIEVE_SETTING']['max_triples_in_total']
AVAIL_ACCEPTED_NTYPES = SETTINGS_PARAMS['RETRIEVE_SETTING']['accepted_nodes_types']

GENERAL_CONFIGS = list(product(
    AVAIL_MAXMNODES, # 0
    AVAIL_MAXTRIPLES_PERQUERY, # 1
    AVAIL_MAXNODE_PERDEPTH, # 2
    AVAIL_MAXEXPLORE_DEPTH, # 3
    AVAIL_MAXTRIPLES_INTOTAL, # 4
    AVAIL_ACCEPTED_NTYPES, # 5
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

        for spec_raw_params in GENERAL_CONFIGS:
            SPECIFIC_PARAMS = deepcopy(SETTINGS_PARAMS)

            # setting specific values for available hyperparameters
            SPECIFIC_PARAMS['DATASET_NAME'] = dataset
            SPECIFIC_PARAMS['KNOWLEDGE_GRAPH_NAME'] = kg_name

            SETTINGS_PARAMS['RETRIEVE_SETTING']['max_matched_nodes'] = spec_raw_params[0]
            SETTINGS_PARAMS['RETRIEVE_SETTING']['max_triples_per_node'] = spec_raw_params[1]
            SETTINGS_PARAMS['RETRIEVE_SETTING']['max_nodes_per_depth'] = spec_raw_params[2]
            SETTINGS_PARAMS['RETRIEVE_SETTING']['max_explore_depth'] = spec_raw_params[3]
            SETTINGS_PARAMS['RETRIEVE_SETTING']['max_triples_in_total'] = spec_raw_params[4]
            SETTINGS_PARAMS['RETRIEVE_SETTING']['accepted_nodes_types'] = spec_raw_params[5]

            # creating name for experiment
            short_ds_name = dataset.split('_')[0]
            short_kg_name = kg_name.split('_')[0]
            exp_id = hashlib.md5(str(SPECIFIC_PARAMS).encode()).hexdigest()[:8]
            prefix = f"N{spec_raw_params[0]}TPR{spec_raw_params[1]}TIT{spec_raw_params[2]}ANT{''.join([str_ntype[0] for str_ntype in spec_raw_params[3]])}"
            SPECIFIC_PARAMS['EXPERIMENT_NAME'] = f"{prefix}_{short_ds_name}_{short_kg_name}(#{exp_id})({SETTINGS_PARAMS['PERSONALAI_VERSION']})"

            # saving generated params-config
            SPEC_PARAMS_SPATH = f"{SAVE_PARAMS_PATH}/{dataset}/{kg_name}/{SPECIFIC_PARAMS['EXPERIMENT_NAME']}.yaml"
            if os.path.exists(SPEC_PARAMS_SPATH):
                print(f"params-file already exists: {SPEC_PARAMS_SPATH}")
                continue

            with open(SPEC_PARAMS_SPATH, 'w') as fd:
                yaml.dump(
                    SPECIFIC_PARAMS, fd,
                    default_flow_style=False,
                    sort_keys=False
                )

print("############ DONE ############")
