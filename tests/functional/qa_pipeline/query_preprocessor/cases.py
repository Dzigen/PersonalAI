import sys
from copy import deepcopy
from functools import reduce
# TO CHANGE
PROJECT_BASE_DIR = '../'
TEST_VOLUME_DIR = './volumes'
sys.path.insert(0, PROJECT_BASE_DIR)

from src.pipelines.qa.query_preprocessing import QueryPreprocessorConfig
from src.pipelines.qa.query_preprocessing.decomposition import QueryDecomposerConfig
from src.pipelines.qa.query_preprocessing.denoising import QueryDenoiserConfig
from src.pipelines.qa.query_preprocessing.enhancing import QueryEnhancerConfig

QUERIES = [ # with mistakes
    "Кгда родился Алксандр Сергеевич Пушкин и как звли его родителей?",
    "Чем отличаются параметры от аргументов функций?",
    "When was Alexander Sergeevich Pushkin born and wht were his parnts names?",
    "What is the difference btween parameters and fnction arguments?"
]

denoise_config = QueryDenoiserConfig()
enhance_config = QueryEnhancerConfig()
decomposition_config = QueryDecomposerConfig()


# query, query preproc config,
QUERY_PREPROC_TEST_CASES = [
    # all none
    QueryPreprocessorConfig(lang='en', denoising_config=None, enhancing_config=None, decomposition_config=None),
    # only decomposer
    QueryPreprocessorConfig(lang='en', denoising_config=None, enhancing_config=None, decomposition_config=decomposition_config),
    # only enhancer
    QueryPreprocessorConfig(lang='en', denoising_config=None, enhancing_config=enhance_config, decomposition_config=None),
    # only denoiser
    QueryPreprocessorConfig(lang='en', denoising_config=denoise_config, enhancing_config=None, decomposition_config=None),
    # only decomposer + enhancer
    QueryPreprocessorConfig(lang='en', denoising_config=None, enhancing_config=enhance_config, decomposition_config=decomposition_config),
    # only decomposer + denoiser
    QueryPreprocessorConfig(lang='en', denoising_config=denoise_config, enhancing_config=None, decomposition_config=decomposition_config),
    # only denoiser + enhancer
    QueryPreprocessorConfig(lang='en', denoising_config=denoise_config, enhancing_config=enhance_config, decomposition_config=None),
    # all not None
    QueryPreprocessorConfig(lang='en', denoising_config=denoise_config, enhancing_config=enhance_config, decomposition_config=decomposition_config),
]

QP_POPULATED_TEST_CASES = []
for query in QUERIES:
    for qpp_config in QUERY_PREPROC_TEST_CASES:
        QP_POPULATED_TEST_CASES.append([query, qpp_config])
