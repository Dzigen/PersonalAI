from dataclasses import dataclass, field
from typing import Tuple, List, Union, Dict

from .searchplan_enhancer import SearchPlanEnhancerConfig, SearchPlanEnhancer
from .entities_extractor import EntitiesExtractorConfig, EntitiesExtractor
from .cluequeries_generator import ClueQueriesGeneratorConfig, ClueQueriesGenerator
from .clueanswer_generator import ClueAnswerGenerator, ClueAnswerGeneratorConfig
from .clueanswers_summarisation import ClueAnswersSummarizerConfig, ClueAnswersSummarizer
from .answer_generator import AnswerGeneratorConfig, AnswerGenerator
from .entities2nodes_matching import Entities2NodesMatcher, Entities2NodesMatcherConfig
from .utils import MediumKGReasonerStages
from .config import MDGR_MAIN_LOG_PATH, CONTINUE_SEARCH_MESSAGE, ANSWER_IS_GENERATED_MESSAGE, MEDIUM_KG_RETRIEVER_CONFIG
from ..utils import AbstractKGReasoner, BaseKGReasonerConfig
from ..weak_reasoner.knowledge_retriever import KnowledgeRetrieverConfig, KnowledgeRetriever
from .....utils.data_structs import create_id, QueryInfo, SearchPlanInfo, NodeInfo
from .....utils import Logger, ReturnInfo, ReturnStatus, update_rinfo
from .....utils.cache_kv import CacheUtils
from .....kg_model import KnowledgeGraphModel
from .....db_drivers.kv_driver import KeyValueDriverConfig
from .....db_drivers.vector_driver import VectorDBInstance
from .....utils.agent_stat_analyzer import AgentStatAnalyzerConfig


@dataclass
class MediumKGReasonerConfig(BaseKGReasonerConfig):
    """Конфигурация medium-версии пайплайна по ризонингу на графе знаний.

    :param searchplan_enhancer_config: Конфигурация стадии #1 reasoner-конвейера: выполняется генерация/модификация плана поиска/извлечения информации (в виде списка запросов на естественном языке) из графа знаний. Значение по умолчанию SearchPlanEnhancerConfig().
    :type searchplan_enhancer_config: SearchPlanEnhancerConfig, optional
    :param entities_extractor_config: Конфигурация стадии #2.1.1 reasoner-конвейера: выполняется извлечение ключевых сущностей из текущего шага/запроса (из плана) поиска. Значение по умолчанию EntitiesExtractorConfig().
    :type entities_extractor_config: EntitiesExtractorConfig, optional
    :param e2n_matcher_config: Конфигурация стадии #2.1.2 reasoner-конвейера: выполняется сопоставление (matching) сущностей из запроса (шага поиска) с объектами в графе знаний. Значение по умолчанию Entities2NodesMatcherConfig().
    :type e2n_matcher_config: Entities2NodesMatcherConfig, optional
    :param cluequeries_generator_config: Конфигурация стадии #2.2 reasoner-конвейера: выполняется генерация детализированных/уточнённых clue-запросов на основе линейной комбинации отобранных object–вершин для текущего запроса (шага поиска). Значение по умолчанию ClueQueriesGeneratorConfig().
    :type cluequeries_generator_config: ClueQueriesGeneratorConfig, optional
    :param knowledge_retriever_config: Конфигурация стадии #3.1.1 reasoner-конвейера: выполняется обход графа знаний, извлечение триплетов, релевантных к текущему clue-запросу, и их фильтрация для формирования концентрированного множества информации. Значение по умолчанию MEDIUM_KG_RETRIEVER_CONFIG.
    :type knowledge_retriever_config: KnowledgeRetrieverConfig, optional
    :param clueanswer_generator_config: Конфигурация стадии #3.1.2 reasoner-конвейера:выполняется резюмирование информации, найденной/извлечённой по каждому clue-запросу в отдельности. Значение по умолчанию ClueAnswerGeneratorConfig().
    :type clueanswer_generator_config: ClueAnswerGeneratorConfig, optional
    :param clueanswers_summarizer_config: Конфигурация стадии #3.2 reasoner-конвейера: выполняется резюмирование информации, полученной врамках обхода графа по clue-запросам, для текущего шага/запроса (в рамках плана) поиска. Значение по умолчанию ClueAnswersSummarizerConfig().
    :type clueanswers_summarizer_config: ClueAnswersSummarizerConfig, optional
    :param answer_generator_config: Конфигурация стадии #4 reasoner-конвейера: выполняется генерация ответа на исходный вопрос, на основании информации, извлечённой из графа знаний по шагам/запросам плана поиска. Значение по умолчанию AnswerGeneratorConfig().
    :type answer_generator_config: AnswerGeneratorConfig, optional
    :param max_searchplan_steps: Максимальное количество шагов плана поиска, по которым может быть выполнен обход/излвечение информации из графа знаний. По достижению заданного предела поиск завершается. Значение по умолчанию 5.
    :type max_searchplan_steps: int, optional
    :param answer_something: Если True, то по достижении предела по количеству выполненных шагов плана будет произведена принудительная генерация ответа на вопрос по извлечённому набору информации (даже если в неё не содержится релевантных материалов для получения правильного ответа); иначе (по достижению предела обработанных шагов поиска) в качества ответа будет сформировна/возвращена NoAnswer-заглушка в качества результата работы reasoner-пайплайна. Значение по умолчанию True.
    :type answer_something: bool, optional
    :param cache_table_name: Название таблицы в структуре (базе) данных, куда будут сохраняться (кешироваться) основные результаты работы MediumKGReasoner-класса. Значение по умолчанию 'qa_mediumreasoner_cache'.
    :type cache_table_name: str, optional
    :param log: Отладочный класс для журналирования/мониторинга поведения инициализируемой компоненты. Значение по умолчанию Logger(MDGR_MAIN_LOG_PATH).
    :type log: Logger, optional
    :param verbose: Если True, то информация о поведении класса будет сохраняться в stdout и файл-журналирования (log), иначе только в файл. Значение по умолчанию False.
    :type verbose: bool, optional
    """
    searchplan_enhancer_config: SearchPlanEnhancerConfig = field(default_factory=lambda: SearchPlanEnhancerConfig())
    entities_extractor_config: EntitiesExtractorConfig = field(default_factory=lambda: EntitiesExtractorConfig())
    e2n_matcher_config: Entities2NodesMatcherConfig = field(default_factory=lambda: Entities2NodesMatcherConfig())

    cluequeries_generator_config: ClueQueriesGeneratorConfig = field(default_factory=lambda: ClueQueriesGeneratorConfig())
    knowledge_retriever_config: KnowledgeRetrieverConfig = field(default_factory=lambda: MEDIUM_KG_RETRIEVER_CONFIG)
    clueanswer_generator_config: ClueAnswerGeneratorConfig = field(default_factory=lambda: ClueAnswerGeneratorConfig())
    clueanswers_summarizer_config: ClueAnswersSummarizerConfig = field(default_factory=lambda: ClueAnswersSummarizerConfig())

    answer_generator_config: AnswerGeneratorConfig = field(default_factory=lambda: AnswerGeneratorConfig())

    max_searchplan_steps: int = 3
    answer_something: bool = True

    cache_table_name: str = 'qa_mediumreasoner_cache'
    log: Logger = field(default_factory=lambda: Logger(MDGR_MAIN_LOG_PATH))
    verbose: bool = False

    def to_str(self) -> str:
        str_spe_config = self.searchplan_enhancer_config.to_str()
        str_ee_config = self.entities_extractor_config.to_str()
        str_e2nm_config = self.e2n_matcher_config.to_str()
        str_cqg_config = self.cluequeries_generator_config.to_str()
        str_kr_config = self.knowledge_retriever_config.to_str()
        str_cag_config = self.cluequeries_generator_config.to_str()
        str_cas_config = self.clueanswers_summarizer_config.to_str()
        str_ag_config = self.answer_generator_config.to_str()

        str_init_configs = f"{str_spe_config}|{str_ee_config}|{str_e2nm_config}"
        str_proc_configs = f"{str_cqg_config}|{str_kr_config}|{str_cag_config}|{str_cas_config}"
        return f"{str_init_configs}|{str_proc_configs}|{str_ag_config}|{self.max_searchplan_steps}|{self.answer_something}"


class MediumKGReasoner(AbstractKGReasoner, CacheUtils):
    """Medium-версия пайплайна по ризонигу на графе знаний с целью извлечения релевантной информации к запросу.

    :param kg_model: Модель памяти (графа знаний) ассистента.
    :type kg_model: KnowledgeGraphModel
    :param config: Конфигурация MediumKGReasoner-пайплайна. Значение по умолчанию MediumKGReasonerConfig().
    :type config: MediumKGReasonerConfig, optional
    :param cache_kvdriver_config: Конфигурация структуры данных для кеширования промежуточных результатов в рамках компонент данного класса. Значение по умолчению None.
    :type cache_kvdriver_config: Union[KeyValueDriverConfig, None], optional
    :param inferencestat_config: Конфигурация компоненты для сбора информации и расчёта статистик по результатам выполнения inference-операциий в рамках LLM-задач. Значение по умолчанию None.
    :type inferencestat_config: Union[None, AgentStatAnalyzerConfig], optional
    """

    def __init__(self, kg_model: KnowledgeGraphModel, config: MediumKGReasonerConfig = MediumKGReasonerConfig(),
                 cache_kvdriver_config: Union[None, KeyValueDriverConfig] = None,
                 inferencestat_config: Union[None, AgentStatAnalyzerConfig] = None) -> None:
        self.config = config
        self.kg_model = kg_model

        self.cachekv = self.init_cachekv(
            cache_kvdriver_config, config.cache_table_name)

        agent = kg_model.AVAILABLE_AGENTS[kg_model.AGENTS_MAP.qa_pipeline]
        self.using_agent_info = {'kw': agent.CONNECTOR_KW, 'config': agent.config}

        self.stages: MediumKGReasonerStages = MediumKGReasonerStages(
            searchplan_enhancer=SearchPlanEnhancer(
                agent, self.config.searchplan_enhancer_config, cache_kvdriver_config, inferencestat_config),
            entities_extractor=EntitiesExtractor(
                agent, self.config.entities_extractor_config, cache_kvdriver_config, inferencestat_config),
            entities2nodes_matcher=Entities2NodesMatcher(
                self.kg_model, self.config.e2n_matcher_config, cache_kvdriver_config),
            cluequeries_generator=ClueQueriesGenerator(
                agent, self.config.cluequeries_generator_config, cache_kvdriver_config, inferencestat_config),
            knowledge_retriever=KnowledgeRetriever(
                self.kg_model, self.config.knowledge_retriever_config, cache_kvdriver_config),
            clueanswer_generator=ClueAnswerGenerator(
                agent, self.config.clueanswer_generator_config, cache_kvdriver_config, inferencestat_config),
            clueanswers_summarizer=ClueAnswersSummarizer(
                agent, self.config.clueanswers_summarizer_config, cache_kvdriver_config, inferencestat_config),
            answer_generator=AnswerGenerator(
                agent, self.config.answer_generator_config, cache_kvdriver_config, inferencestat_config)
        )

        self.log = config.log
        self.verbose = config.verbose

    def update_searchplan(self, search_step: int, search_plan: SearchPlanInfo) -> Tuple[SearchPlanInfo, ReturnInfo]:
        self.log(
            f"CURRENT SEARCH STEP: {search_step} / {self.config.max_searchplan_steps}", verbose=self.verbose)
        search_plan, rinfo = self.stages.searchplan_enhancer.perform(
            search_step, search_plan)
        if rinfo.status != ReturnStatus.success:
            self.log("Operation ended with error!", verbose=self.verbose)
            self.log(
                f"RESULT:\n- {rinfo.status}\n- {search_plan}", verbose=self.config.verbose)
        else:
            self.log("Operation ended successfully", verbose=self.verbose)
            str_searchsteps = '\n'.join(
                [f'{i}. {step}' for i, step in enumerate(search_plan.search_steps)])
            self.log(f"RESULT:\n{str_searchsteps}",
                     verbose=self.config.verbose)

        return search_plan, rinfo

    def match_searchstep_to_kg(self, search_query: str) -> Tuple[Dict[str, List[VectorDBInstance]], ReturnInfo]:
        matched_kg_objects, rinfo = None, ReturnInfo()
        self.log("STAGE#2.1.1 - ENTITIES EXTRACTION",
                 verbose=self.config.verbose)
        entities, ee_rinfo = self.stages.entities_extractor.perform(search_query)
        if ee_rinfo.status == ReturnStatus.success:
            self.log("Operation ended successfully", verbose=self.verbose)
            self.log(f"RESULT: {entities}", verbose=self.config.verbose)
        else:
            self.log("Operation ended with error!", verbose=self.verbose)
        update_rinfo(rinfo, ee_rinfo)

        if rinfo.status == ReturnStatus.success:
            self.log("STAGE#2.1.2 - ENTITIES-TO-KGOBJECTS MATCHING",
                     verbose=self.config.verbose)
            matched_kg_objects, e2nm_rinfo = self.stages.entities2nodes_matcher.perform(entities)
            if e2nm_rinfo.status == ReturnStatus.success:
                self.log("Operation ended successfully", verbose=self.verbose)
                str_matched_kgobject = '\n'.join([f'- [{entitie}][{len(objects)}] ' + ', '.join(list(map(lambda obj: obj.text, objects))) for entitie, objects in matched_kg_objects.items()])
                self.log(f"RESULT:\n{str_matched_kgobject}", verbose=self.config.verbose)
            else:
                self.log("Operation ended with error!", verbose=self.verbose)
            update_rinfo(rinfo, e2nm_rinfo)
        else:
            self.log("During previous steps error occurs.",
                     verbose=self.verbose)

        return matched_kg_objects, rinfo

    def get_cluequeries(self, search_query: str, matched_kg_objects: Dict[str, List[NodeInfo]]) -> Tuple[List[QueryInfo], ReturnInfo]:
        cluequeries, rinfo = self.stages.cluequeries_generator.perform(
            search_query, matched_kg_objects)
        str_cluequeries = '\n'.join(
            [f'- [{list(map(lambda obj: obj.text, clueq.linked_nodes))}] {clueq.query}' for clueq in cluequeries])
        if rinfo.status == ReturnStatus.success:
            self.log("Operation ended successfully", verbose=self.verbose)
            self.log(
                f"RESULT: {len(cluequeries)}\n{str_cluequeries}", verbose=self.config.verbose)
        else:
            self.log("Operation ended with error!", verbose=self.verbose)

        return cluequeries, rinfo

    def search_clueanswers(self, search_query: str, cluequeries: List[QueryInfo]) -> Tuple[List[str], ReturnInfo]:
        clueanswers, rinfo = [], ReturnInfo()
        for j, cur_cluequery in enumerate(cluequeries):
            self.log(
                f"Current clue-query ({j} / {len(cluequeries)}): {cur_cluequery.query}", verbose=self.config.verbose)
            self.log(
                f"Current clue-query id: {create_id(cur_cluequery.query)}", verbose=self.config.verbose)

            self.log("STAGE#3.1.1 - KNOWLEDGE RETRIEVING",
                     verbose=self.config.verbose)
            retrieved_triplets, rk_rinfo = self.stages.knowledge_retriever.retrieve(cur_cluequery)
            update_rinfo(rinfo, rk_rinfo)
            if rinfo.status == ReturnStatus.success:
                self.log("Operation ended successfully", verbose=self.verbose)
                self.log(f"RESULT: {len(retrieved_triplets)}",
                         verbose=self.config.verbose)
                for triplet in retrieved_triplets:
                    self.log(f"* {triplet}", verbose=self.config.verbose)
            else:
                self.log("Operation ended with error!", verbose=self.verbose)
                break

            self.log("STAGE#3.1.2 - CLUE-ANSWER GENERATION",
                     verbose=self.config.verbose)
            cur_clueanswer, cag_rinfo = self.stages.clueanswer_generator.perform(
                search_query, retrieved_triplets)
            update_rinfo(rinfo, cag_rinfo)
            if rinfo.status == ReturnStatus.success:
                self.log("Operation ended successfully", verbose=self.verbose)
                self.log(f"RESULT: {cur_clueanswer}",
                         verbose=self.config.verbose)
            else:
                self.log("Operation ended with error!", verbose=self.verbose)
                break

            clueanswers.append(cur_clueanswer)

        return clueanswers, rinfo

    def summarize_clueanswers(self, search_query: str, cluequeries: List[QueryInfo], clueanswers: List[str]) -> Tuple[str, ReturnInfo]:
        search_step_answer, rinfo = self.stages.clueanswers_summarizer.perform(
            search_query, list(map(lambda cq_info: cq_info.query, cluequeries)), clueanswers)
        if rinfo.status == ReturnStatus.success:
            self.log("Operation ended successfully", verbose=self.verbose)
        else:
            self.log("Operation ended with error!", verbose=self.verbose)

        return search_step_answer, rinfo

    def answer_generation_trying(self, search_plan: SearchPlanInfo) -> Tuple[Union[str, None], ReturnInfo]:
        answer, rinfo = self.stages.answer_generator.perform(search_plan)
        if rinfo.status == ReturnStatus.success:
            self.log("Operation ended successfully", verbose=self.verbose)
            self.log(f"RESULT: {answer}", verbose=self.config.verbose)
        else:
            self.log("Operation ended with error!", verbose=self.verbose)

        return answer, rinfo

    def forced_answer_generation(self, search_plan: SearchPlanInfo) -> Tuple[Union[str, None], ReturnInfo]:
        answer, rinfo = None, ReturnInfo()
        if self.config.answer_something:
            self.log("Пытаемся сгенерировать ответа на основе имеющейся информации...",
                     verbose=self.config.verbose)
            answer, rinfo.status = self.stages.answer_generator.tasks_solvers.answer_gen_solver.solve(
                lang=self.stages.answer_generator.config.lang, search_plan=search_plan)
        else:
            self.log("В рамках заданных ограничений поиска не удалось сгенерировать релевантный ответ.",
                     verbose=self.config.verbose)
            answer = "<|NotEnoughtInfo|>"

        if rinfo.status == ReturnStatus.success:
            self.log("Operation ended successfully", verbose=self.verbose)
        else:
            self.log("Operation ended with error!", verbose=self.verbose)

        return answer, rinfo

    def prepare_searchqueries(self, search_query: str, search_step: int) -> Tuple[List[QueryInfo], ReturnInfo]:
        cluequeries, rinfo = None, ReturnInfo()
        self.log("STAGE#2.1 - SEARCH-STEP to KG MATCHING",
                 verbose=self.config.verbose)
        self.log(
            f"Current step #{search_step}: {search_query}", verbose=self.config.verbose)
        matched_kg_objects, ssm_rinfo = self.match_searchstep_to_kg(
            search_query)
        update_rinfo(rinfo, ssm_rinfo)

        self.log("STAGE#2.2 - CLUE-QUERIES GENERATION",
                 verbose=self.config.verbose)
        if rinfo.status == ReturnStatus.success:
            cluequeries, cqg_rinfo = self.get_cluequeries(
                search_query, matched_kg_objects)
            update_rinfo(rinfo, cqg_rinfo)
        else:
            self.log("During previous steps error occurs.",
                     verbose=self.verbose)

        return cluequeries, rinfo

    def traverse_kg(self, search_query: str, cluequeries: List[QueryInfo]) -> Tuple[Union[str, None], ReturnInfo]:
        search_step_answer, rinfo = None, ReturnInfo()
        self.log("STAGE#3.1 - RETRIEVING INFORMATION FROM KG BASED ON CLUE-QUERIES",
                 verbose=self.config.verbose)
        clueanswers, cag_rinfo = self.search_clueanswers(
            search_query, cluequeries)
        update_rinfo(rinfo, cag_rinfo)

        self.log("STAGE#3.2 - CLUE-ANSWERS SUMMARISATION",
                 verbose=self.config.verbose)
        if rinfo.status == ReturnStatus.success:
            search_step_answer, cas_rinfo = self.summarize_clueanswers(
                search_query, cluequeries, clueanswers)
            update_rinfo(rinfo, cas_rinfo)
        else:
            self.log("During previous steps error occurs.",
                     verbose=self.verbose)

        return search_step_answer, rinfo

    def get_cache_key(self, query: str) -> List[str]:
        str_using_agent_config = f"{self.using_agent_info['kw']}:{self.using_agent_info['config'].to_str()}"
        return [self.config.to_str(), str_using_agent_config, query]

    @CacheUtils.cache_method_output
    def perform(self, query: str) -> Tuple[str, ReturnInfo]:
        """Метод предназначен для выполнения ризонинга на графе знаний с помощью указанного запроса с целью извлечения релевантной информации.

        :param query: запрос на естественном языке.
        :type query: str
        :return: Кортеж из двух объектов: (1) извлечённая/релевантная информация/ответа на запрос; (2) статус завершения операции с пояснительной информацией.
        :rtype: Tuple[str, ReturnInfo]
        """
        self.log("START MEDIUM KG-REASONING...", verbose=self.config.verbose)
        self.log(
            f"BASE_QUESTION ID: {create_id(query)}", verbose=self.config.verbose)
        self.log(f"BASE_QUESTION: {query}", verbose=self.config.verbose)
        answer, rinfo = None, ReturnInfo()
        search_plan = SearchPlanInfo(base_query=query)

        self.log("Start iterative search...", verbose=self.verbose)
        for search_step in range(self.config.max_searchplan_steps):

            self.log("STAGE#1 - SEARCH PLAN INITING/ENHANCING",
                     verbose=self.config.verbose)
            search_plan, usp_rinfo = self.update_searchplan(
                search_step, search_plan)
            update_rinfo(rinfo, usp_rinfo)

            self.log("STAGE#2 - QUERIES PREPARATION FOR KG TRAVERSAL",
                     verbose=self.config.verbose)
            if rinfo.status == ReturnStatus.success:
                search_query = search_plan.search_steps[search_step]
                cluequeries, psq_rinfo = self.prepare_searchqueries(
                    search_query, search_step)
                update_rinfo(rinfo, psq_rinfo)
            else:
                self.log("During previous steps error occurs.",
                         verbose=self.verbose)
                break

            self.log("STAGE#3 - KG TRAVERSAL FOR RELEVANT KNOWLEDGE EXTRACTION",
                     verbose=self.config.verbose)
            if rinfo.status == ReturnStatus.success:
                search_step_answer, tkg_rinfo = self.traverse_kg(
                    search_query, cluequeries)
                update_rinfo(rinfo, tkg_rinfo)

                if rinfo.status == ReturnStatus.success:
                    search_plan.steps_answers.append(search_step_answer)
            else:
                self.log("During previous steps error occurs.",
                         verbose=self.verbose)
                break

            self.log("STAGE#4 - ANSWER-GENERATION TRYING",
                     verbose=self.config.verbose)
            if rinfo.status == ReturnStatus.success:
                answer, agt_rinfo = self.answer_generation_trying(search_plan)
                update_rinfo(rinfo, agt_rinfo)

                if answer is not None:
                    self.log(ANSWER_IS_GENERATED_MESSAGE,
                             verbose=self.config.verbose)
                    break
                else:
                    self.log(CONTINUE_SEARCH_MESSAGE,
                             verbose=self.config.verbose)
            else:
                self.log("During previous steps error occurs.",
                         verbose=self.verbose)
                break

        self.log("Завершаем поиск.", verbose=self.config.verbose)
        self.log(
            f"Информация по выполненному поиску: {search_plan}", verbose=self.config.verbose)
        if answer is None and rinfo.status == ReturnStatus.success:
            answer, fag_rinfo = self.forced_answer_generation(search_plan)
            update_rinfo(rinfo, fag_rinfo)

        self.log(f"RETURNED ANSWER: {answer}", verbose=self.config.verbose)
        self.log(f"STATUS: {rinfo.status}", verbose=self.config.verbose)

        return answer, rinfo
