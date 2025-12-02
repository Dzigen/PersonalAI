from ..weak_reasoner.knowledge_retriever import KnowledgeRetrieverConfig
from ..weak_reasoner.knowledge_retriever.traversal_methods import MixturedGraphSearchConfig, GraphBeamSearchConfig
from .....utils.data_structs import NodeType

MDGR_MAIN_LOG_PATH = 'log/qa/kg_reasoner/medium/main'

CONTINUE_SEARCH_MESSAGE = "Недостаточно информации для генерации релевантного ответа на вопрос. Продолжаем поиск."
ANSWER_IS_GENERATED_MESSAGE = "Удалось сгененирвоать ответа на вопрос. Завершаем поиск."

MEDIUM_KG_RETRIEVER_CONFIG = KnowledgeRetrieverConfig(
    retriever_method='mixture',
    retriever_config=MixturedGraphSearchConfig(
        retriever1_name='beamsearch',
        retriever1_config=GraphBeamSearchConfig(
            max_depth=1,
            max_paths=20,
        ),
        accepted_node_types=[NodeType.hyper, NodeType.episodic, NodeType.time]
    )
)
