from funcs import *
from utils import ReaderMetrics

############### Генерация ответов ###############

S4_META = {
    "LOAD_FILTERED_TRIPLETS_VERSION": "v4",
    "SAVE_GEN_ANSWERS_VERSION": "v14",
    "QUESTION_PROMPT_TEMPLATE": PROMPT_QA_TEMPLATE,
    "TRPLETE_PROMPT_TEMPLATES": {
        "manufacturer": "device: {d}, company: {c}",
        "opinion": "person: {p}, device: {d}, opinion: {o}, feature: {f}",
        'has_device': "person: {p}, has device: {d}"
    },
    "MAX_LIST_LEN": -1
}

save_log_dir = f"{SAVE_STAGE4_LOGDIR}/{S4_META['SAVE_GEN_ANSWERS_VERSION']}" 
load_log_tmpdata_dir = f"{SAVE_STAGE3_1_LOGDIR}/{S4_META['LOAD_FILTERED_TRIPLETS_VERSION']}/{LOG_TMPDATA_DIRNAME}"
save_log_tmpdata_dir = f"{save_log_dir}/{LOG_TMPDATA_DIRNAME}"
save_log_metafile = f"{save_log_dir}/{LOG_META_FILENMAE}"

check_create_dir(save_log_dir)
check_create_dir(save_log_tmpdata_dir)

qa_files = os.listdir(EVAL_DATADIR)
for qa_file in qa_files:
    generate_answers_from_triplets_file(
        qa_file, load_log_tmpdata_dir, save_log_tmpdata_dir, S4_META, EVAL_DATADIR)
    gc.collect()
    
save_json(S4_META, save_log_metafile)

############### Оценка качеста ###############

SF_META = {
    'LOAD_GEN_ANSWERS_VERSION': "v14",
    'SAVE_SCORES_VERSION': "v14"
}

METRICS = ReaderMetrics(base_dir=UTILS_DIR)

save_log_dir = f"{SAVE_SCORES_LOGDIR}/{SF_META['SAVE_SCORES_VERSION']}" 
save_log_metafile = f"{save_log_dir}/{LOG_META_FILENMAE}"
save_log_tmpdata_dir = f"{save_log_dir}/{LOG_SCORES_DIRNAME}"
gen_answers_dir = f'{SAVE_STAGE4_LOGDIR}/{SF_META["LOAD_GEN_ANSWERS_VERSION"]}/{LOG_TMPDATA_DIRNAME}'

check_create_dir(save_log_dir)
check_create_dir(save_log_tmpdata_dir)

qa_files = os.listdir(EVAL_DATADIR)
for qa_file in tqdm(qa_files):
    measure_quality_from_answers_file(qa_file, gen_answers_dir, save_log_tmpdata_dir, EVAL_DATADIR, METRICS)

save_json(SF_META, save_log_metafile)