from dataclasses import dataclass, field
from typing import Tuple, List

from .searchplan_enhancer import SearchPlanEnhancerConfig, SearchPlanEnhancer
from .entities_extractor import EntitiesExtractorConfig, EntitiesExtractor
from .cluequeries_generator import ClueQueriesGeneratorConfig, ClueQueriesGenerator
from .clueanswers_summarisation import ClueAnswersSummarizerConfig, ClueAnswersSummarizer
from .answer_generator import AnswerGeneratorConfig, AnswerGenerator
from .entities2nodes_matching import Entities2NodesMatcher, Entities2NodesMatcherConfig

from .utils import SearchPlanInfo
from .config import MDGR_MAIN_LOG_PATH
from ..utils import AbstractKGReasoner, BaseKGReasonerConfig
from ..weak_reasoner.knowledge_retriever import KnowledgeRetrieverConfig, KnowledgeRetriever
from ..weak_reasoner.answer_generator import QALLMGeneratorConfig, QALLMGenerator
from .....utils.data_structs import create_id
from .....utils import Logger, ReturnInfo, ReturnStatus
from .....kg_model import KnowledgeGraphModel
from .....db_drivers.kv_driver import KeyValueDriverConfig

@dataclass
class MediumKGReasonerConfig(BaseKGReasonerConfig):

    searchplan_enhancer_config: SearchPlanEnhancerConfig = field(default_factory=lambda: SearchPlanEnhancerConfig())
    entities_extractor_config: EntitiesExtractorConfig = field(default_factory=lambda: EntitiesExtractorConfig())
    e2n_matcher_config: Entities2NodesMatcherConfig = field(default_factory=lambda: Entities2NodesMatcherConfig())

    cluequeries_generator_config: ClueQueriesGeneratorConfig = field(default_factory=lambda: ClueQueriesGeneratorConfig())
    knowledge_retriever_config: KnowledgeRetrieverConfig = field(default_factory=lambda: KnowledgeRetrieverConfig())
    clueanswer_generator_config: QALLMGeneratorConfig = field(default_factory=lambda: QALLMGeneratorConfig())
    clueanswers_summarizer_confif: ClueAnswersSummarizerConfig = field(default_factory=lambda: ClueAnswersSummarizerConfig())

    answer_generator_config: AnswerGeneratorConfig = field(default_factory=lambda: AnswerGeneratorConfig())

    max_searchplan_steps: int = 10

    log: Logger = field(default_factory=lambda: Logger(MDGR_MAIN_LOG_PATH))
    verbose: bool = False

class MediumKGReasoner(AbstractKGReasoner):

    def __init__(self, kg_model: KnowledgeGraphModel, config: MediumKGReasonerConfig = MediumKGReasonerConfig(),
                 cache_kvdriver_config: KeyValueDriverConfig = None):
        self.config = config
        self.kg_model = kg_model
        
        self.searchplan_enhancer = SearchPlanEnhancer(self.config.searchplan_enhancer_config, cache_kvdriver_config)
        
        self.entities_extractor = EntitiesExtractor(self.config.entities_extractor_config, cache_kvdriver_config)
        self.entities2nodes_matcher = Entities2NodesMatcher(self.kg_model, self.config.e2n_matcher_config, cache_kvdriver_config)

        self.cluequeries_generator = ClueQueriesGenerator(self.config.clueanswer_generator_config, cache_kvdriver_config)
        self.knowledge_retriever = KnowledgeRetriever(self.kg_model, self.config.knowledge_retriever_config, cache_kvdriver_config)
        self.clueanswer_generator = QALLMGenerator(self.config.clueanswer_generator_config, cache_kvdriver_config)
        self.clueanswers_summariser = ClueAnswersSummarizer(self.config.clueanswers_summarizer_confif, cache_kvdriver_config)

        self.answer_generator = AnswerGenerator(self.config.answer_generator_config, cache_kvdriver_config)

        self.log = config.log
        self.verbose = config.verbose

    def clear_kv_caches(self):
        # TODO
        pass

    def perform(self, query: str) -> Tuple[str, ReturnInfo]:
        self.log("START MEDIUM KG-REASONING...", verbose=self.config.verbose)
        self.log(f"BASE_QUESTION ID: {create_id(query)}", verbose=self.config.verbose)
        self.log(f"BASE_QUESTION: {query}", verbose=self.config.verbose)
        answer, info = None, ReturnInfo()
        search_plan = SearchPlanInfo(base_query=query)

        self.log("Start iterative search...", verbose=self.verbose)
        for search_step in range(self.config.max_searchplan_steps):
            self.log(f"CURRENT SEARCH ITERATION: {search_step} / {self.config.max_searchplan_steps}", verbose=self.verbose)

            self.log("STAGE#1 - SEARCH PLAN INITING/ENHANCING", verbose=self.config.verbose)
            search_plan, info = self.searchplan_enhancer.perform(search_step, search_plan)
            str_searchsteps = '\n'.join([ f'{i}. {step}' for i, step in enumerate(search_plan.search_steps)])
            self.log(f"RESULT:\n{str_searchsteps}", verbose=self.config.verbose)
            if info.status != ReturnStatus.success:
                break
            
            search_query = search_plan.search_steps[search_step]
            self.log(f"Current step #{search_step}: {search_query}")

            self.log("STAGE#2.1 - ENTITIES EXTRACTION", verbose=self.config.verbose)
            entities, info = self.entities_extractor.perform(search_query)
            self.log(f"RESULT: {entities}", verbose=self.config.verbose)
            if info.status != ReturnStatus.success:
                break

            self.log("STAGE#2.2 - ENTITIES-TO-KGOBJECTS MATCHING", verbose=self.config.verbose)
            matched_kg_objects = self.entities2nodes_matcher.perform(entities)
            str_matched_kgobject = '\n'.join([f'- [{entitie}][{len(objects)}] ' + ', '.join(list(map(lambda obj: obj.document))) for entitie, objects in matched_kg_objects.items()])
            self.log(f"RESULT:\n{str_matched_kgobject}", verbose=self.config.verbose)

            self.log("STAGE#3 - CLUE-QUERIES GENERATION", verbose=self.config.verbose)
            cluequeries, info = self.cluequeries_generator.perform(search_query, matched_kg_objects)
            str_cluequeries = '\n'.join([f'- [{list(map(lambda obj: obj.document, clueq.linked_nodes))}] {clueq.query}' for clueq in cluequeries])
            self.log(f"RESULT: {len(cluequeries)}\n{str_cluequeries}", verbose=self.config.verbose)
            if info.status != ReturnStatus.success:
                break

            self.log("STAGE#4 - RETRIEVING INFORMATION FROM KG BASED ON CLUE-QUERIES", verbose=self.config.verbose)
            clueanswers = []
            error_occurred = False
            for cur_cluequery in cluequeries:
                self.log(f"Current clue-query: {cur_cluequery.query}", verbose=self.config.verbose)
                self.log(f"Current clue-query id: {create_id(cur_cluequery.query)}", verbose=self.config.verbose)
            
                self.log("STAGE#4.1 - KNOWLEDGE RETRIEVING", verbose=self.config.verbose)
                retrieved_triplets, info = self.knowledge_retriever.retrieve(cur_cluequery)
                self.log(f"RESULT: {len(retrieved_triplets)}", verbose=self.config.verbose)
                for triplet in retrieved_triplets:
                    self.log(f"* {triplet}", verbose=self.config.verbose)
                if info.status != ReturnStatus.success:
                    error_occurred = True
                    break

                self.log("STAGE#4.2 - CLUE-ANSWER GENERATION", verbose=self.config.verbose)
                cur_clueanswer, info = self.clueanswer_generator.generate(cur_cluequery.query, retrieved_triplets)
                self.log(f"RESULT: {cur_clueanswer}", verbose=self.config.verbose)
                if info.status != ReturnStatus.success:
                    error_occurred = True
                    break
                
                clueanswers.append(cur_clueanswer)

            if error_occurred:
                break
            
            self.log("STAGE#4 - CLUE-ANSWERS SUMMARISATION", verbose=self.config.verbose)
            search_step_answer, info = self.clueanswers_summariser.perform(search_query, cluequeries, clueanswers)
            self.log(f"RESULT: {search_step_answer}", verbose=self.config.verbose)
            if info.status != ReturnStatus.success:
                break
            else:
                search_plan.steps_answers.append(search_step_answer)
            
            self.log("STAGE#5 - ANSWER-GENERATION TRYING", verbose=self.config.verbose)
            answer, info = self.answer_generator(search_plan)
            self.log(f"RESULT: {answer}", verbose=self.config.verbose)
            if info.status != ReturnStatus.success:
                break

            #
            if answer is not None:
                self.log("Удалось сгененирвоать ответа на вовпрос. Завершаем поиск.")
                break
            else:
                self.log("Недостаточно информации для генерации релевантного ответа на вопрос. Продолжаем поиск.")

        if answer is None and info.status == ReturnStatus.success:
            self.log("В рамках заданных ограничений поиска не удалось сгенерировать релевантный ответ.")
            answer = "<|NotEnoughtInfo|>"

        self.log(f"RETURNED ANSWER: {answer}", verbose=self.config.verbose)
        self.log(f"STATUS: {info.status}", verbose=self.config.verbose)            

        return answer, info
