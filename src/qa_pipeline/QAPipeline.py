from ..agents.llama_agent import LLaMAagent
from ..knowledge_graph_model import KnowledgeGraphModel
from .utils import QAPipelineConfig

from answer_generator import QALLMGenerator
from knowledge_retriever import KnowledgeRetriever
from knowledge_comparator import KnowledgeComparator
from query_parser import QueryLLMParser

class QAPipeline:
    """Главный класс QA-конвейера по генерации ответов 
    на основании имеющегося графа знаний
    """

    def __init__(self, kg_model: KnowledgeGraphModel, llm_agent: LLaMAagent, config: QAPipelineConfig) -> None:
        self.kg_model = kg_model
        self.llama_agent = llm_agent
        self.config = config

        self.query_parser = QueryLLMParser(self.config.query_parser_config)
        self.knowledge_comparator = KnowledgeComparator(self.config.knowledge_comparator_config)
        self.knowledge_retriever = KnowledgeRetriever(self.config.knowledge_retriever_config)
        self.answer_generator = QALLMGenerator(self.config.answer_generator_config)

    def answer(self, query: str) -> str:
        # stage 1
        query_info = self.query_parser.extract_entities(query)
        # stage 2
        self.knowledge_comparator.link_kgnodes_to_query(query_info)
        # stage 3
        retrieved_triplets = self.knowledge_retriever.retrieve(query_info)
        # stage 4
        context = self.answer_generator.formate_context(retrieved_triplets)
        answer = self.answer_generator.generate(query_info.query, context)

        return answer