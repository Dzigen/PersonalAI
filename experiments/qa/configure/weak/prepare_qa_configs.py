import sys
import yaml
import joblib

from src.pipelines.qa.query_preprocessing.decomposition.agent_tasks.query_decomposition import AgentQueryDecompTaskConfigSelector
from src.pipelines.qa.query_preprocessing.decomposition.agent_tasks.decomposition_classifier import AgentDecompClsTaskConfigSelector
from src.pipelines.qa.query_preprocessing.decomposition import QueryDecomposerConfig


from src.pipelines.qa.query_preprocessing import QueryPreprocessorConfig

from src.pipelines.qa.kg_reasoning.weak_reasoner.answer_generator.agent_tasks.ag import AgentSimpleAGTaskConfigSelector
from src.pipelines.qa.kg_reasoning.weak_reasoner.query_parser.agent_tasks.kw_extraction import AgentKWETaskConfigSelector
from src.pipelines.qa.kg_reasoning.weak_reasoner import QueryLLMParserConfig, KnowledgeComparatorConfig, \
    KnowledgeRetrieverConfig, QALLMGeneratorConfig

from src.pipelines.qa.answers_aggregation.agent_tasks.answers_summarisation import AgentSubASummTaskConfigSelector
from src.pipelines.qa.answers_aggregation import AnswersAggregatorConfig
from src.pipelines.qa.kg_reasoning.weak_reasoner import WeakKGReasonerConfig

# Read YAML file (specexp-params)
SPECEXP_PARAMS_FILEP = sys.orig_argv[2]
with open(SPECEXP_PARAMS_FILEP, 'r') as stream:
    SPECEXP_PARAMS = yaml.safe_load(stream)

# Read YAML file (expdir-params)
EXPDIR_PARAMS_FILEP = sys.orig_argv[3]
with open(EXPDIR_PARAMS_FILEP, 'r') as stream:
    EXPDIR_PARAMS = yaml.safe_load(stream)

sys.path.insert(0, EXPDIR_PARAMS['WORKSPACE_CONTAINER_DIRS']['base_path'])

################ hyperparams #####################

EXP_RESULTS_DIR = f"{EXPDIR_PARAMS['BASE_PERSONALAI_PATH']}/{EXPDIR_PARAMS['WORKSPACE_CONTAINER_DIRS']['experiments']}/{EXPDIR_PARAMS['WORKSPACE_CONTAINER_DIRS']['results']}"
EXP_KG_PATH = f"{EXP_RESULTS_DIR}/{SPECEXP_PARAMS['DATASET_NAME']}/{SPECEXP_PARAMS['KNOWLEDGE_GRAPH_NAME']}"
SPEC_EXPERIMENT_DIR = f"{EXP_KG_PATH}/{EXPDIR_PARAMS['EXPERIMENT_NAME']}"

QPREPROC_CONFIG_SPATH = f"{SPEC_EXPERIMENT_DIR}/{EXPDIR_PARAMS['EXP_SAVE_FILES']['qpreproc_config']}"
KG_REASONSER_CONFIG_SPATH = f"{SPEC_EXPERIMENT_DIR}/{EXPDIR_PARAMS['EXP_SAVE_FILES']['kgreasoner_config']}"
ANSWAGGR_CONFIG_SPATH = f"{SPEC_EXPERIMENT_DIR}/{EXPDIR_PARAMS['EXP_SAVE_FILES']['aaggregator_configg']}"

################ QUERY PREPROCESSOR ################

qdenoiser_config = Quer

if PARAMS['BASE_KGR_CONFIG']['query_preprocessing']['decomposition_config'] == 'None':
    decomposition_config = None
else:
    decomposition_config = QueryDecomposerConfig(
        lang=PARAMS['BASE_KGR_CONFIG']['lang'], adriver_config=adriver_config,
        classify_agent_task_config=AgentDecompClsTaskConfigSelector.select(
            base_config_version=PARAMS['BASE_KGR_CONFIG']['query_preprocessing']['decomposition_config']['classify_agent_task_version']),
        decompose_agent_task_config=AgentQueryDecompTaskConfigSelector.select(
            base_config_version=PARAMS['BASE_KGR_CONFIG']['query_preprocessing']['decomposition_config']['decompose_agent_task_version']))

querypreproc_config = QueryPreprocessorConfig(
    denoising_config=None,
    enhancing_config=None,
    decomposition_config=decomposition_config
)

################ ANSWER AGGREGATOR ################

answeraggr_config = AnswersAggregatorConfig(
    lang=PARAMS['BASE_KGR_CONFIG']['lang'], adriver_config=adriver_config,
    suba_summarisation_agent_task_config=AgentSubASummTaskConfigSelector.select(
        base_config_version=PARAMS['BASE_KGR_CONFIG']['answers_aggregation']['suba_summarisation_agent_task_version']))

################ KG REASONER ################

if PARAMS['WEAK_KG_REASONER']['knowledge_retriever_config']['filter_method'] == 'None':
    filter_method = None
    filter_config = None
else:
    filter_method = PARAMS['WEAK_KG_REASONER']['knowledge_retriever_config']['filter_method']
    filter_config = PARAMS['WEAK_KG_REASONER']['knowledge_retriever_config']['filter_config']

k_retriever_config = KnowledgeRetrieverConfig(
    retriever_method=PARAMS['WEAK_KG_REASONER']['knowledge_retriever_config']['retriever_method'],
    retriever_config=PARAMS['WEAK_KG_REASONER']['knowledge_retriever_config']['retriever_config'],
    filter_method=filter_method, filter_config=filter_config)

if PARAMS['WEAK_KG_REASONER']['query_parser_config'] == 'None':
    query_parser_config = None
    knowledge_comparator_config = None
else:
    query_parser_config = QueryLLMParserConfig(
        lang=PARAMS['BASE_KGR_CONFIG']['lang'],
        adriver_config=adriver_config,
        kw_extraction_task_config=AgentKWETaskConfigSelector.select(
            base_config_version=PARAMS['WEAK_KG_REASONER']['query_parser_config']['kw_extraction_task']['prompts_version']))
    knowledge_comparator_config = KnowledgeComparatorConfig(
        **PARAMS['WEAK_KG_REASONER']['knowledge_comparator_config'])

kg_reasoner_config = WeakKGReasonerConfig(
    query_parser_config=query_parser_config,
    knowledge_comparator_config=knowledge_comparator_config,
    knowledge_retriever_config=k_retriever_config,
    answer_generator_config=QALLMGeneratorConfig(
        lang=PARAMS['BASE_KGR_CONFIG']['lang'],
        adriver_config=adriver_config,
        ag_task_config=AgentSimpleAGTaskConfigSelector.select(
            base_config_version=PARAMS['WEAK_KG_REASONER']['answer_generator_config']['ag_task']['prompts_version'])))

################ SAVING CONFIGS ################

# вывести полученный конфиг в stdout
print("Полученная query_preproc-конфигурация:")
print(querypreproc_config)
print("Полученная kg_reasoner-конфигурация:")
print(kg_reasoner_config)
print("Полученная answers_aggr-конфигурация:")
print(answeraggr_config)

# сохранить полученный конфиг в директорию соответствующего эксперимента
with open(QPREPROC_CONFIG_SPATH, 'wb') as fd:
    joblib.dump(querypreproc_config, fd)
with open(KG_REASONSER_CONFIG_SPATH, 'wb') as fd:
    joblib.dump(kg_reasoner_config, fd)
with open(ANSWAGGR_CONFIG_SPATH, 'wb') as fd:
    joblib.dump(answeraggr_config, fd)

print("############ DONE ############")
