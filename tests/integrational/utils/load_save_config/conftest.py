import pytest

import sys
# TO CHANGE
PROJECT_BASE_DIR = '../'
TEST_VOLUME_DIR = './volumes'
sys.path.insert(0, PROJECT_BASE_DIR)

# db drivers
from src.db_drivers.graph_driver.GraphDriver import GraphDriverConfig
from src.db_drivers.graph_driver.utils import GraphDBConnectionConfig
from src.db_drivers.kv_driver.KeyValueDriver import KeyValueDriverConfig
from src.db_drivers.kv_driver.utils import KVDBConnectionConfig
from src.db_drivers.table_driver.TableDriver import TableDriverConfig
from src.db_drivers.table_driver.utils import TableDBConnectionConfig
from src.db_drivers.tree_driver.TreeDriver import TreeDriverConfig
from src.db_drivers.tree_driver.utils import TreeDBConnectionConfig
from src.db_drivers.vector_driver.VectorDriver import VectorDriverConfig
from src.db_drivers.vector_driver.utils import VectorDBConnectionConfig
from src.db_drivers.vector_driver.embedders import EmbedderModelConfig

# agent
from src.agents.utils import AgentConnectorConfig
from src.agents.AgentDriver import AgentDriverConfig

# !!! PAY ATTENTION !!!
# reranker
#from src.rerankers.RerankerDriver import RerankerDriverConfig
#from src.rerankers.methods.EnsembleFusionReranker import EnsembleFusionRerankerConfig
#from src.rerankers.methods.MultiStepReranker import MultiStepRerankerConfig
#from src.rerankers.methods.SingleStepReranker import SingleStepRerankerConfig

# graph traversal
from src.pipelines.qa.kg_reasoning.weak_reasoner.knowledge_retriever.traversal_methods.AStarTripletsRetriever import AStarMetricsConfig
from src.pipelines.qa.kg_reasoning.weak_reasoner.knowledge_retriever.traversal_methods.AStarTripletsRetriever import AStarGraphSearchConfig
from src.pipelines.qa.kg_reasoning.weak_reasoner.knowledge_retriever.traversal_methods.BeamSearchTripletsRetriever import GraphBeamSearchConfig
from src.pipelines.qa.kg_reasoning.weak_reasoner.knowledge_retriever.traversal_methods.MixturedTripletsRetriever import MixturedGraphSearchConfig
from src.pipelines.qa.kg_reasoning.weak_reasoner.knowledge_retriever.traversal_methods.NaiveBFSTripletsRetriever import NaiveBFSGraphSearchConfig
from src.pipelines.qa.kg_reasoning.weak_reasoner.knowledge_retriever.traversal_methods.NaiveTripletsRetriever import NaiveGraphSearchConfig
from src.pipelines.qa.kg_reasoning.weak_reasoner.knowledge_retriever.traversal_methods.WaterCirclesTripletsRetriever import WaterCirclesSearchConfig

# triples filtering
from src.pipelines.qa.kg_reasoning.weak_reasoner.knowledge_retriever.filtering_methods.TripletsFilter import TripletsFilterConfig

# stat_analyzer
from src.utils.agent_stat_analyzer.AgentStatAnalyzer import AgentStatAnalyzerConfig

# main
from src.main import PersonalAIConfig

# textidstore
from src.TextIdStore import TextIdStoreConfig

# kg_model
from src.kg_model.KnowledgeGraphModel import KnowledgeGraphModelConfig
from src.kg_model.nodestree_model.NodesTreeModel import NodesTreeModelConfig
from src.kg_model.nodestree_model.utils import NodesTreeModelAgentTasksConfig
from src.kg_model.graph_model.GraphModel import GraphModelConfig
from src.kg_model.embeddings_model.EmbeddingsModel import EmbeddingsModelConfig

# qa_pipeline
from src.pipelines.qa.QAPipeline import QAPipelineConfig

## preprocessor
from src.pipelines.qa.query_preprocessing.QueryPreprocessor import QueryPreprocessorConfig
from src.pipelines.qa.query_preprocessing.denoising.QueryDenoiser import QueryDenoiserConfig
from src.pipelines.qa.query_preprocessing.denoising.utils import QueryDenoiserAgentTasksConfig
from src.pipelines.qa.query_preprocessing.enhancing.QueryEnhancer import QueryEnhancerConfig
from src.pipelines.qa.query_preprocessing.enhancing.utils import QueryEnhancerAgentTasksConfig
from src.pipelines.qa.query_preprocessing.decomposition.QueryDecomposer import QueryDecomposerConfig
from src.pipelines.qa.query_preprocessing.decomposition.utils import QueryDecomposerAgentTasksConfig

## reasoner
from src.pipelines.qa.kg_reasoning.KGReasoner import KnowledgeGraphReasonerConfig

from src.pipelines.qa.kg_reasoning.weak_reasoner.WeakKGReasoner import WeakKGReasonerConfig
from src.pipelines.qa.kg_reasoning.weak_reasoner.query_parser.QueryLLMParser import QueryLLMParserConfig
from src.pipelines.qa.kg_reasoning.weak_reasoner.query_parser.utils import QueryLLMParserAgentTasksConfig
from src.pipelines.qa.kg_reasoning.weak_reasoner.knowledge_comparator.KnowledgeComparator import KnowledgeComparatorConfig
from src.pipelines.qa.kg_reasoning.weak_reasoner.knowledge_retriever.KnowledgeRetriever import KnowledgeRetrieverConfig
from src.pipelines.qa.kg_reasoning.weak_reasoner.answer_generator.QALLMGenerator import QALLMGeneratorConfig
from src.pipelines.qa.kg_reasoning.weak_reasoner.answer_generator.utils import QALLMGeneratorAgentTasksConfig

from src.pipelines.qa.kg_reasoning.medium_reasoner.MediumKGReasoner import MediumKGReasonerConfig
from src.pipelines.qa.kg_reasoning.medium_reasoner.searchplan_enhancer.SearchPlanEnhancer import SearchPlanEnhancerConfig
from src.pipelines.qa.kg_reasoning.medium_reasoner.searchplan_enhancer.utils import SearchPlanEnhancerAgentTasksConfig
from src.pipelines.qa.kg_reasoning.medium_reasoner.entities_extractor.EntitiesExtractor import EntitiesExtractorConfig
from src.pipelines.qa.kg_reasoning.medium_reasoner.entities_extractor.utils import EntitiesExtractorAgentTasksConfig
from src.pipelines.qa.kg_reasoning.medium_reasoner.entities2nodes_matching.Entities2NodesMatcher import Entities2NodesMatcherConfig
from src.pipelines.qa.kg_reasoning.medium_reasoner.cluequeries_generator.ClueQueriesGenerator import ClueQueriesGeneratorConfig
from src.pipelines.qa.kg_reasoning.medium_reasoner.cluequeries_generator.utils import ClueQueriesGeneratorAgentTasksConfig
from src.pipelines.qa.kg_reasoning.medium_reasoner.clueanswer_generator.ClueAnswerGenerator import ClueAnswerGeneratorConfig
from src.pipelines.qa.kg_reasoning.medium_reasoner.clueanswer_generator.utils import ClueAnswerGeneratorAgentTasksConfig
from src.pipelines.qa.kg_reasoning.medium_reasoner.clueanswers_summarisation.ClueAnswersSummarizer import ClueAnswersSummarizerConfig
from src.pipelines.qa.kg_reasoning.medium_reasoner.clueanswers_summarisation.utils import ClueAnswersSummarizerAgentTasksConfig
from src.pipelines.qa.kg_reasoning.medium_reasoner.answer_generator.AnswerGenerator import AnswerGeneratorConfig
from src.pipelines.qa.kg_reasoning.medium_reasoner.answer_generator.utils import AnswerGeneratorAgentTasksConfig

## aggregator
from src.pipelines.qa.answers_aggregation.AnswersAggregator import AnswersAggregatorConfig
from src.pipelines.qa.answers_aggregation.utils import AnswersAggregatorAgentTasksConfig

# mem_pipeline
from src.pipelines.memorize.MemPipeline import MemPipelineConfig
from src.pipelines.memorize.extractor.LLMExtractor import LLMExtractorConfig
from src.pipelines.memorize.extractor.utils import MemExtractorAgentTasksConfig
from src.pipelines.memorize.updator.LLMUpdator import LLMUpdatorConfig
from src.pipelines.memorize.updator.utils import MemUpdatorAgentTasksConfig

# ============================================================

AVAILABLE_CONFIGS = {
    'db': {
        'graph': {
            'driver': GraphDriverConfig,
            'conn': GraphDBConnectionConfig
        },
        'kv': {
            'driver': KeyValueDriverConfig,
            'conn': KVDBConnectionConfig
        },
        'table': {
            'driver': TableDriverConfig,
            'conn': TableDBConnectionConfig
        },
        'tree': {
            'driver': TreeDriverConfig,
            'conn': TreeDBConnectionConfig
        },
        'vector': {
            'driver': VectorDriverConfig,
            'conn': VectorDBConnectionConfig,
            'embedder': EmbedderModelConfig
        }
    },
    'agent': {
        'driver': AgentDriverConfig,
        'conn': AgentConnectorConfig
    },
    # 'rerankers': {
    #     'driver': RerankerDriverConfig,
    #     'single_step': SingleStepRerankerConfig,
    #     'multi_step': MultiStepRerankerConfig,
    #     'ensemble': EnsembleFusionRerankerConfig
    # },
    'stat_analyzer': AgentStatAnalyzerConfig,

    'main': PersonalAIConfig,
    'textidstore': TextIdStoreConfig,
    'kg_model': {
        'main': KnowledgeGraphModelConfig,
        'graph': GraphModelConfig,
        'embedder': EmbeddingsModelConfig,
        'tree': {
            'main': NodesTreeModelConfig,
            'agent_tasks': NodesTreeModelAgentTasksConfig
        }
    },
    'qa_pipeline': {
        'main': QAPipelineConfig,
        'preprocessor': {
            'main': QueryPreprocessorConfig,
            'denoise': {
                'main': QueryDenoiserConfig,
                'agent_tasks': QueryDenoiserAgentTasksConfig
            },
            'enhance': {
                'main': QueryEnhancerConfig,
                'agent_tasks': QueryEnhancerAgentTasksConfig
            },
            'decompose': {
                'main': QueryDecomposerConfig,
                'agent_tasks': QueryDecomposerAgentTasksConfig
            },
        },
        'reasoner': {
            'main': KnowledgeGraphReasonerConfig,
            'weak': {
                'main': WeakKGReasonerConfig,
                'parser': {
                    'main': QueryLLMParserConfig,
                    'agent_tasks': QueryLLMParserAgentTasksConfig
                },
                'comparator': KnowledgeComparatorConfig,
                'retriever': KnowledgeRetrieverConfig,
                'generator': {
                    'main': QALLMGeneratorConfig,
                    'agent_tasks': QALLMGeneratorAgentTasksConfig
                }
            },
            'medium': {
                'main': MediumKGReasonerConfig,
                'plan_enh': {
                    'main': SearchPlanEnhancerConfig,
                    'agent_tasks': SearchPlanEnhancerAgentTasksConfig
                },
                'entities': {
                    'main': EntitiesExtractorConfig,
                    'agent_tasks': EntitiesExtractorAgentTasksConfig
                },
                'matching': Entities2NodesMatcherConfig,
                'clueq_gen': {
                    'main': ClueQueriesGeneratorConfig,
                    'agent_tasks': ClueQueriesGeneratorAgentTasksConfig
                },
                'cluea_gen': {
                    'main': ClueAnswerGeneratorConfig,
                    'agent_tasks': ClueAnswerGeneratorAgentTasksConfig
                },
                'cluea_summ': {
                    'main': ClueAnswersSummarizerConfig,
                    'agent_tasks': ClueAnswersSummarizerAgentTasksConfig
                },
                'answr_gen': {
                    'main': AnswerGeneratorConfig,
                    'agent_tasks': AnswerGeneratorAgentTasksConfig
                }
            },
            'graph_traversal': {
                'astarmetrics': AStarMetricsConfig,
                'astar': AStarGraphSearchConfig,
                'beamsearch': GraphBeamSearchConfig,
                'mixture': MixturedGraphSearchConfig,
                'bfs': NaiveBFSGraphSearchConfig,
                'naiveretriever': NaiveGraphSearchConfig,
                'watercircles': WaterCirclesSearchConfig
            },
            'graph_filtering': {
                'naive': TripletsFilterConfig
            },
        },
        'aggregator': {
            'main': AnswersAggregatorConfig,
            'agent_tasks': AnswersAggregatorAgentTasksConfig
        }
    },
    'mem_pipeline': {
        'main': MemPipelineConfig,
        'extractor': {
            'main': LLMExtractorConfig,
            'agent_tasks': MemExtractorAgentTasksConfig
        },
        'updator': {
            'main': LLMUpdatorConfig,
            'agent_tasks': MemUpdatorAgentTasksConfig,
        }
    }

}
