from ...knowledge_retriever import KnowledgeRetrieverConfig
from ...knowledge_retriever.traversal_methods import MixturedGraphSearchConfig, GraphBeamSearchConfig, NaiveGraphSearchConfig
from ...knowledge_retriever.filtering_methods import TripletsFilterConfig
from .....rerankers import RerankerDriverConfig
from .....rerankers.methods.EnsembleFusionReranker import EnsembleFusionRerankerConfig, RetrieverConfig
from .....utils.data_structs import NodeType


MDGR_MAIN_LOG_PATH = 'log/qa/kg_reasoner/medium/main'

CONTINUE_SEARCH_MESSAGE = "Недостаточно информации для генерации релевантного ответа на вопрос. Продолжаем поиск."
ANSWER_IS_GENERATED_MESSAGE = "Удалось сгененирвоать ответа на вопрос. Завершаем поиск."

MEDIUM_KG_RETRIEVER_CONFIG = KnowledgeRetrieverConfig(
    retriever_method='mixture',
    retriever_config=MixturedGraphSearchConfig(
        retriever1_name='beamsearch',
        retriever1_config=GraphBeamSearchConfig(
            max_depth=3,
            max_paths=10,
        ),
        retriever2_name='naive_retriever',
        retriever2_config=NaiveGraphSearchConfig(
            max_k=25
        ),
        accepted_node_types=[NodeType.object, NodeType.hyper, NodeType.episodic, NodeType.time]
    ),
    filter_method='naive',
    filter_config=TripletsFilterConfig(
        max_k=25,
        reranker_driver_config=RerankerDriverConfig(
            name='ensemble_fusion',
            strategy_config=EnsembleFusionRerankerConfig(
                vdb_names=['dense_triplets', 'bm25_triplets'],
                retriever_configs=[RetrieverConfig(fetch_n=25, threshold=0.5), RetrieverConfig(fetch_n=25, threshold=0.5)],
                weights=[0.9, 0.1]
            )
        )
    )
)
