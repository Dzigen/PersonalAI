# генерируем kg_reasoner конфиг на основании params.yaml файла

import sys
import yaml
import joblib

# Read YAML file
PARAMS_FILEP = sys.orig_argv[2]
with open(PARAMS_FILEP, 'r') as stream:
    PARAMS = yaml.safe_load(stream)

sys.path.insert(0, PARAMS['WORKSPACE_CONTAINER_DIRS']['base_path'])

from src.pipelines.qa.kg_reasoning.weak_reasoner import WeakKGReasonerConfig
from src.pipelines.qa.kg_reasoning.weak_reasoner import QueryLLMParserConfig, KnowledgeComparatorConfig, \
    KnowledgeRetrieverConfig, QALLMGeneratorConfig
from src.pipelines.qa.kg_reasoning.weak_reasoner.query_parser.agent_tasks.kw_extraction import AgentKWETaskConfigSelector
from src.pipelines.qa.kg_reasoning.weak_reasoner.answer_generator.agent_tasks.ag import AgentSimpleAGTaskConfigSelector
from src.agents import AgentDriverConfig
from src.agents.utils import AgentConnectorConfig

#
from src.pipelines.qa.answers_aggregation import AnswersAggregatorConfig
from src.pipelines.qa.answers_aggregation.agent_tasks.answers_summarisation import AgentSubASummTaskConfigSelector

from src.pipelines.qa.query_preprocessing import QueryPreprocessorConfig
from src.pipelines.qa.query_preprocessing.decomposition import QueryDecomposerConfig
from src.pipelines.qa.query_preprocessing.decomposition.agent_tasks.decomposition_classifier import AgentDecompClsTaskConfigSelector
from src.pipelines.qa.query_preprocessing.decomposition.agent_tasks.query_decomposition import AgentQueryDecompTaskConfigSelector

from src.pipelines.qa.kg_reasoning.medium_reasoner import MediumKGReasonerConfig
from src.pipelines.qa.kg_reasoning.medium_reasoner.searchplan_enhancer import SearchPlanEnhancerConfig
from src.pipelines.qa.kg_reasoning.medium_reasoner.searchplan_enhancer.agent_tasks.enhance_classifier import AgentEnhanceClassifierTaskConfigSelector
from src.pipelines.qa.kg_reasoning.medium_reasoner.searchplan_enhancer.agent_tasks.plan_enhancer import AgentPlanEnhancingTaskConfigSelector
from src.pipelines.qa.kg_reasoning.medium_reasoner.searchplan_enhancer.agent_tasks.plan_initializer import AgentPlanInitTaskConfigSelector

from src.pipelines.qa.kg_reasoning.medium_reasoner.entities_extractor import EntitiesExtractorConfig
from src.pipelines.qa.kg_reasoning.medium_reasoner.entities_extractor.agent_tasks.entities_extractor import AgentEntitiesExtrTaskConfigSelector

from src.pipelines.qa.kg_reasoning.medium_reasoner.entities2nodes_matching import Entities2NodesMatcherConfig

from src.pipelines.qa.kg_reasoning.medium_reasoner.cluequeries_generator import ClueQueriesGeneratorConfig
from src.pipelines.qa.kg_reasoning.medium_reasoner.cluequeries_generator.agent_tasks.query_generator import AgentCQueryGenTaskConfigSelector
from src.pipelines.qa.kg_reasoning.medium_reasoner.clueanswer_generator import ClueAnswerGeneratorConfig
from src.pipelines.qa.kg_reasoning.medium_reasoner.clueanswer_generator.agent_tasks.clueanswer_generation import AgentClueAnswerGenTaskConfigSelector

from src.pipelines.qa.kg_reasoning.medium_reasoner.clueanswers_summarisation import ClueAnswersSummarizerConfig
from src.pipelines.qa.kg_reasoning.medium_reasoner.clueanswers_summarisation.agent_tasks.answers_summarisation import AgentClueAnswersSummTaskConfigSelector

from src.pipelines.qa.kg_reasoning.medium_reasoner.answer_generator import AnswerGeneratorConfig
from src.pipelines.qa.kg_reasoning.medium_reasoner.answer_generator.agent_tasks.answer_generator import AgentAnswerGeneratorTaskConfigSelector
from src.pipelines.qa.kg_reasoning.medium_reasoner.answer_generator.agent_tasks.answer_trying_classifier import AgentAnswerClassifierTaskConfigSelector

################ hyperparams #####################

DS_EXPERIMENT_DIR = f"{PARAMS['WORKSPACE_CONTAINER_DIRS']['base_path']}/{PARAMS['WORKSPACE_CONTAINER_DIRS']['experiments']}/{PARAMS['WORKSPACE_CONTAINER_DIRS']['exp_results']}/{PARAMS['DATASET_NAME']}"
SPEC_EXPERIMENT_DIR = f"{DS_EXPERIMENT_DIR}/{PARAMS['EXPERIMENT_NAME']}"
KG_REASONSER_CONFIG_SPATH = f"{SPEC_EXPERIMENT_DIR}/{PARAMS['SAVE_CONFIGS_NAMES']['kg_reasoner_config']}"
QPREPROC_CONFIG_SPATH = f"{SPEC_EXPERIMENT_DIR}/{PARAMS['SAVE_CONFIGS_NAMES']['querypreproc_config']}"
ANSWAGGR_CONFIG_SPATH = f"{SPEC_EXPERIMENT_DIR}/{PARAMS['SAVE_CONFIGS_NAMES']['answeraggr_config']}"

################ agent driver config #####################

adriver_config = AgentDriverConfig(
    name=PARAMS['BASE_KGR_CONFIG']['agent_config']['vendor'],
    agent_config=AgentConnectorConfig(
        gen_strategy=PARAMS['BASE_KGR_CONFIG']['agent_config']['gen_strategy'],
        credentials=PARAMS['BASE_KGR_CONFIG']['agent_config']['credentials'],
        ext_params=PARAMS['BASE_KGR_CONFIG']['agent_config']['ext_params']))

################ KG REASONER ################

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

answeraggr_config = AnswersAggregatorConfig(
    lang=PARAMS['BASE_KGR_CONFIG']['lang'], adriver_config=adriver_config,
    suba_summarisation_agent_task_config=AgentSubASummTaskConfigSelector.select(
        base_config_version=PARAMS['BASE_KGR_CONFIG']['answers_aggregation']['suba_summarisation_agent_task_version']))

if PARAMS['BASE_KGR_CONFIG']['name'] == 'weak':

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

elif PARAMS['BASE_KGR_CONFIG']['name'] == 'medium':

    if PARAMS['MEDIUM_KG_REASONER']['knowledge_retriever_config']['filter_method'] == 'None':
        filter_method = None
        filter_config = None
    else:
        filter_method = PARAMS['MEDIUM_KG_REASONER']['knowledge_retriever_config']['filter_method']
        filter_config = PARAMS['MEDIUM_KG_REASONER']['knowledge_retriever_config']['filter_config']

    k_retriever_config = KnowledgeRetrieverConfig(
        retriever_method=PARAMS['MEDIUM_KG_REASONER']['knowledge_retriever_config']['retriever_method'],
        retriever_config=PARAMS['MEDIUM_KG_REASONER']['knowledge_retriever_config']['retriever_config'],
        filter_method=filter_method, filter_config=filter_config)

    kg_reasoner_config = MediumKGReasonerConfig(
        searchplan_enhancer_config=SearchPlanEnhancerConfig(
            lang=PARAMS['BASE_KGR_CONFIG']['lang'], adriver_config=adriver_config,
            plan_initing_agent_task_config=AgentPlanInitTaskConfigSelector.select(
                base_config_version=PARAMS['MEDIUM_KG_REASONER']['searchplan_enhancer_config']['plan_initing_agent_task_version']
            ),
            enhance_classifier_agent_task_config=AgentEnhanceClassifierTaskConfigSelector.select(
                base_config_version=PARAMS['MEDIUM_KG_REASONER']['searchplan_enhancer_config']['enhance_classifier_agent_task_version']
            ),
            plan_enhancing_agent_task_config=AgentPlanEnhancingTaskConfigSelector.select(
                base_config_version=PARAMS['MEDIUM_KG_REASONER']['searchplan_enhancer_config']['plan_enhancing_agent_task_version']
            )
        ),
        entities_extractor_config=EntitiesExtractorConfig(
            lang=PARAMS['BASE_KGR_CONFIG']['lang'], adriver_config=adriver_config,
            entities_extraction_agent_task_config=AgentEntitiesExtrTaskConfigSelector.select(
                base_config_version=PARAMS['MEDIUM_KG_REASONER']['entities_extractor_config']['entities_extraction_agent_task_version']
            )
        ),
        e2n_matcher_config=Entities2NodesMatcherConfig(
            use_tree=PARAMS['MEDIUM_KG_REASONER']['e2n_matcher_config']['use_tree'],
            distance_threshold=PARAMS['MEDIUM_KG_REASONER']['e2n_matcher_config']['distance_threshold'],
            max_n=PARAMS['MEDIUM_KG_REASONER']['e2n_matcher_config']['max_n'],
            fetch_k=PARAMS['MEDIUM_KG_REASONER']['e2n_matcher_config']['fetch_k']
        ),
        cluequeries_generator_config=ClueQueriesGeneratorConfig(
            lang=PARAMS['BASE_KGR_CONFIG']['lang'], adriver_config=adriver_config,
            cquerie_generator_agent_task_config=AgentCQueryGenTaskConfigSelector.select(
                base_config_version=PARAMS['MEDIUM_KG_REASONER']['cluequeries_generator_config']['cquerie_generator_agent_task_version']
            )
        ),
        knowledge_retriever_config=k_retriever_config,
        clueanswer_generator_config=ClueAnswerGeneratorConfig(
            lang=PARAMS['BASE_KGR_CONFIG']['lang'], adriver_config=adriver_config,
            cagen_agent_task_config=AgentClueAnswerGenTaskConfigSelector.select(
                base_config_version=PARAMS['MEDIUM_KG_REASONER']['clueanswer_generator_config']['canswer_generator_agent_task_version']
            )
        ),
        clueanswers_summarizer_confif=ClueAnswersSummarizerConfig(
            lang=PARAMS['BASE_KGR_CONFIG']['lang'], adriver_config=adriver_config,
            canswers_summarisation_agent_task_config=AgentClueAnswersSummTaskConfigSelector.select(
                base_config_version=PARAMS['MEDIUM_KG_REASONER']['clueanswers_summarizer_confif']['canswers_summarisation_agent_task_version']
            )
        ),
        answer_generator_config=AnswerGeneratorConfig(
            lang=PARAMS['BASE_KGR_CONFIG']['lang'], adriver_config=adriver_config,
            answer_classifier_agent_task_config=AgentAnswerClassifierTaskConfigSelector.select(
                base_config_version=PARAMS['MEDIUM_KG_REASONER']['answer_generator_config']['answer_classifier_agent_task_version']
            ),
            answer_generator_agent_task_config=AgentAnswerGeneratorTaskConfigSelector.select(
                base_config_version=PARAMS['MEDIUM_KG_REASONER']['answer_generator_config']['answer_generator_agent_task_version']
            )
        ),
        max_searchplan_steps=PARAMS['MEDIUM_KG_REASONER']['max_searchplan_steps']
    )
else:
    raise ValueError

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
