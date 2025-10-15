from ..weak_reasoner.knowledge_retriever import KnowledgeRetrieverConfig
from ..weak_reasoner.knowledge_retriever.traversal_methods import GraphBeamSearchConfig

MDGR_MAIN_LOG_PATH = 'log/qa/kg_reasoner/medium/main'

CONTINUE_SEARCH_MESSAGE = "Недостаточно информации для генерации релевантного ответа на вопрос. Продолжаем поиск."
ANSWER_IS_GENERATED_MESSAGE = "Удалось сгененирвоать ответа на вопрос. Завершаем поиск."

MEDIUM_KG_RETRIEVER_CONFIG = KnowledgeRetrieverConfig(
    retriever_method='beamsearch',
    retriever_config=GraphBeamSearchConfig(
        max_depth=2,
        max_paths=5,
        diff_paths_intersection_by_rel=False,
        same_path_intersection_by_node=False
    )
)
