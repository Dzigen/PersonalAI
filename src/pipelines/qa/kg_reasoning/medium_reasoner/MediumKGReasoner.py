from dataclasses import dataclass, field
from typing import Tuple, List, Union, Dict
from copy import deepcopy

from .searchplan_enhancer import SearchPlanEnhancerConfig, SearchPlanEnhancer
from .entities_extractor import EntitiesExtractorConfig, EntitiesExtractor
from .cluequeries_generator import ClueQueriesGeneratorConfig, ClueQueriesGenerator
from .clueanswer_generator import ClueAnswerGenerator, ClueAnswerGeneratorConfig
from .clueanswers_summarisation import ClueAnswersSummarizerConfig, ClueAnswersSummarizer
from .answer_generator import AnswerGeneratorConfig, AnswerGenerator
from .entities2nodes_matching import Entities2NodesMatcher, Entities2NodesMatcherConfig
from .utils import MediumKGReasonerStages, RelInfoFoundBehaviour, PlanLimitExceededBehaviour
from .config import MDGR_MAIN_LOG_PATH, CONTINUE_SEARCH_MESSAGE, ANSWER_IS_GENERATED_MESSAGE, MEDIUM_KG_RETRIEVER_CONFIG
from ..utils import AbstractKGReasoner, BaseKGReasonerConfig
from ...knowledge_retriever import KnowledgeRetrieverConfig, KnowledgeRetriever
from .....utils.data_structs import create_id, QueryInfo, SearchPlanInfo, BaseComponentConfig, LanguageConfig, NodeInfo, TripletCreator
from .....utils import Logger, ReturnInfo, ReturnStatus, update_rinfo, accumulate_stage_info, \
    CompositeModuleDetailedResult, ModuleType, CompositeModuleResult
from .....utils.cache_kv import CacheUtils
from .....kg_model import KnowledgeGraphModel
from .....db_drivers.kv_driver import KeyValueDriverConfig
from .....db_drivers.vector_driver import VectorDBInstance
from .....utils.agent_stat_analyzer import AgentStatAnalyzerConfig


@dataclass
class MediumKGReasonerConfig(BaseKGReasonerConfig, BaseComponentConfig, LanguageConfig):
    """Конфигурация medium-версии пайплайна по ризонингу на графе знаний.

    :param searchplan_enhancer_config: Конфигурация стадии #1 reasoner-конвейера: выполняется генерация/модификация плана поиска/извлечения информации (в виде списка запросов на естественном языке) из графа знаний. Значение по умолчанию SearchPlanEnhancerConfig().
    :type searchplan_enhancer_config: Union[SearchPlanEnhancerConfig, Dict], optional
    :param entities_extractor_config: Конфигурация стадии #2.1.1 reasoner-конвейера: выполняется извлечение ключевых сущностей из текущего шага/запроса (из плана) поиска. Значение по умолчанию EntitiesExtractorConfig().
    :type entities_extractor_config: Union[EntitiesExtractorConfig, Dict], optional
    :param e2n_matcher_config: Конфигурация стадии #2.1.2 reasoner-конвейера: выполняется сопоставление (matching) сущностей из запроса (шага поиска) с объектами в графе знаний. Значение по умолчанию Entities2NodesMatcherConfig().
    :type e2n_matcher_config: Union[Entities2NodesMatcherConfig, Dict], optional
    :param cluequeries_generator_config: Конфигурация стадии #2.2 reasoner-конвейера: выполняется генерация детализированных/уточнённых clue-запросов на основе линейной комбинации отобранных object–вершин для текущего запроса (шага поиска). Значение по умолчанию ClueQueriesGeneratorConfig().
    :type cluequeries_generator_config: Union[ClueQueriesGeneratorConfig, Dict], optional
    :param knowledge_retriever_config: Конфигурация стадии #3.1.1 reasoner-конвейера: выполняется обход графа знаний, извлечение триплетов, релевантных к текущему clue-запросу, и их фильтрация для формирования концентрированного множества информации. Значение по умолчанию MEDIUM_KG_RETRIEVER_CONFIG.
    :type knowledge_retriever_config: Union[KnowledgeRetrieverConfig, Dict], optional
    :param clueanswer_generator_config: Конфигурация стадии #3.1.2 reasoner-конвейера: выполняется резюмирование информации, найденной/извлечённой по каждому clue-запросу в отдельности. Значение по умолчанию ClueAnswerGeneratorConfig().
    :type clueanswer_generator_config: Union[ClueAnswerGeneratorConfig, Dict], optional
    :param clueanswers_summarizer_config: Конфигурация стадии #3.2 reasoner-конвейера: выполняется резюмирование информации, полученной в рамках обхода графа по clue-запросам, для текущего шага/запроса (в рамках плана) поиска. Значение по умолчанию ClueAnswersSummarizerConfig().
    :type clueanswers_summarizer_config: Union[ClueAnswersSummarizerConfig, Dict], optional
    :param answer_generator_config: Конфигурация стадии #4 reasoner-конвейера: выполняется генерация ответа на исходный вопрос, на основании информации, извлечённой из графа знаний по шагам/запросам плана поиска. Значение по умолчанию AnswerGeneratorConfig().
    :type answer_generator_config: Union[AnswerGeneratorConfig, Dict], optional
    :param max_searchplan_steps: Максимальное количество шагов плана поиска, по которым может быть выполнен обход/излвечение информации из графа знаний. По достижению заданного предела поиск завершается. Значение по умолчанию 5.
    :type max_searchplan_steps: int, optional
    :param enable_searchplan_steps_check: ... . Значение по умолчанию True.
    :type enable_searchplan_steps_check: bool, optional
    :param planlimit_exceeded_behaviour: ... . Значение по умолчанию PlanLimitExceededBehaviour.strict_answer
    :type planlimit_exceeded_behaviour: PlanLimitExceededBehaviour
    :param cache_table_name: Название таблицы в структуре (базе) данных, куда будут сохраняться (кешироваться) основные результаты работы MediumKGReasoner-класса. Значение по умолчанию 'qa_mediumreasoner_cache'.
    :type cache_table_name: str, optional
    """
    searchplan_enhancer_config: Union[SearchPlanEnhancerConfig, Dict] = field(default_factory=lambda: SearchPlanEnhancerConfig())
    entities_extractor_config: Union[EntitiesExtractorConfig, Dict] = field(default_factory=lambda: EntitiesExtractorConfig())
    e2n_matcher_config: Union[Entities2NodesMatcherConfig, Dict] = field(default_factory=lambda: Entities2NodesMatcherConfig())

    cluequeries_generator_config: Union[ClueQueriesGeneratorConfig, Dict] = field(default_factory=lambda: ClueQueriesGeneratorConfig())
    knowledge_retriever_config: Union[KnowledgeRetrieverConfig, Dict] = field(default_factory=lambda: MEDIUM_KG_RETRIEVER_CONFIG)
    clueanswer_generator_config: Union[ClueAnswerGeneratorConfig, Dict] = field(default_factory=lambda: ClueAnswerGeneratorConfig())
    clueanswers_summarizer_config: Union[ClueAnswersSummarizerConfig, Dict] = field(default_factory=lambda: ClueAnswersSummarizerConfig())

    answer_generator_config: Union[AnswerGeneratorConfig, Dict] = field(default_factory=lambda: AnswerGeneratorConfig())

    max_searchplan_steps: int = 6
    enable_searchplan_steps_check: bool = True
    planlimit_exceeded_behaviour: PlanLimitExceededBehaviour = PlanLimitExceededBehaviour.strict_answer

    cache_table_name: str = 'qa_mediumreasoner_cache'
    log_path: str = MDGR_MAIN_LOG_PATH

    def to_str(self) -> str:
        str_spe_config = self.searchplan_enhancer_config.to_str()
        str_ee_config = self.entities_extractor_config.to_str()
        str_e2nm_config = self.e2n_matcher_config.to_str()
        str_cqg_config = self.cluequeries_generator_config.to_str()
        str_kr_config = self.knowledge_retriever_config.to_str()
        str_cag_config = self.clueanswer_generator_config.to_str()
        str_cas_config = self.clueanswers_summarizer_config.to_str()
        str_ag_config = self.answer_generator_config.to_str()

        str_init_configs = f"{str_spe_config}|{str_ee_config}|{str_e2nm_config}"
        str_proc_configs = f"{str_cqg_config}|{str_kr_config}|{str_cag_config}|{str_cas_config}"
        return f"{str_init_configs}|{str_proc_configs}|{str_ag_config}|{self.max_searchplan_steps}|{self.enable_searchplan_steps_check}|{self.planlimit_exceeded_behaviour}"

    @staticmethod
    def from_dict(dict_config: Dict):
        dictconfig_copy = deepcopy(dict_config)
        formated_config = MediumKGReasonerConfig(**dictconfig_copy)
        formated_config.formate_fields()
        return formated_config

    def formate_fields(self):
        if isinstance(self.searchplan_enhancer_config, dict):
            self.searchplan_enhancer_config = SearchPlanEnhancerConfig.from_dict(self.searchplan_enhancer_config)
        else:
            self.searchplan_enhancer_config.formate_fields()
        if isinstance(self.entities_extractor_config, dict):
            self.entities_extractor_config = EntitiesExtractorConfig.from_dict(self.entities_extractor_config)
        else:
            self.entities_extractor_config.formate_fields()
        if isinstance(self.e2n_matcher_config, dict):
            self.e2n_matcher_config = Entities2NodesMatcherConfig.from_dict(self.e2n_matcher_config)
        else:
            self.e2n_matcher_config.formate_fields()

        if isinstance(self.cluequeries_generator_config, dict):
            self.cluequeries_generator_config = ClueQueriesGeneratorConfig.from_dict(self.cluequeries_generator_config)
        else:
            self.cluequeries_generator_config.formate_fields()
        if isinstance(self.knowledge_retriever_config, dict):
            self.knowledge_retriever_config = KnowledgeRetrieverConfig.from_dict(self.knowledge_retriever_config)
        else:
            self.knowledge_retriever_config.formate_fields()
        if isinstance(self.clueanswer_generator_config, dict):
            self.clueanswer_generator_config = ClueAnswerGeneratorConfig.from_dict(self.clueanswer_generator_config)
        else:
            self.clueanswer_generator_config.formate_fields()
        if isinstance(self.clueanswers_summarizer_config, dict):
            self.clueanswers_summarizer_config = ClueAnswersSummarizerConfig.from_dict(self.clueanswers_summarizer_config)
        else:
            self.clueanswers_summarizer_config.formate_fields()

        if isinstance(self.answer_generator_config, dict):
            self.answer_generator_config = AnswerGeneratorConfig.from_dict(self.answer_generator_config)
        else:
            self.answer_generator_config.formate_fields()

        if isinstance(self.planlimit_exceeded_behaviour, str):
            self.planlimit_exceeded_behaviour = PlanLimitExceededBehaviour[self.planlimit_exceeded_behaviour]


class MediumKGReasoner(AbstractKGReasoner, CacheUtils):
    """Medium-версия пайплайна по ризонигу на графе знаний с целью извлечения релевантной информации к запросу.

    :param kg_model: Модель памяти (графа знаний) ассистента.
    :type kg_model: KnowledgeGraphModel
    :param config: Конфигурация MediumKGReasoner-пайплайна. Значение по умолчанию MediumKGReasonerConfig().
    :type config: Union[MediumKGReasonerConfig,Dict], optional
    :param cache_kvdriver_config: Конфигурация структуры данных для кеширования промежуточных результатов в рамках компонент данного класса. Значение по умолчению None.
    :type cache_kvdriver_config: Union[KeyValueDriverConfig, None], optional
    :param inferencestat_config: Конфигурация компоненты для сбора информации и расчёта статистик по результатам выполнения inference-операциий в рамках LLM-задач. Значение по умолчанию None.
    :type inferencestat_config: Union[None, AgentStatAnalyzerConfig], optional
    """

    def __init__(self, kg_model: KnowledgeGraphModel, config: Union[MediumKGReasonerConfig, Dict] = MediumKGReasonerConfig(),
                 cache_kvdriver_config: Union[None, KeyValueDriverConfig] = None,
                 inferencestat_config: Union[None, AgentStatAnalyzerConfig] = None) -> None:
        if isinstance(config, dict):
            config: MediumKGReasonerConfig = MediumKGReasonerConfig.from_dict(config)
        else:
            config.formate_fields()
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

        self.log = Logger(config.log_path)
        self.verbose = config.verbose
        self.log_level = config.log_level

    def update_searchplan(self, search_step: int, search_plan: SearchPlanInfo) -> Tuple[SearchPlanInfo, ReturnInfo, CompositeModuleResult]:
        self.log.debug("CURRENT SEARCH STEP: %d / %d", search_step, self.config.max_searchplan_steps, verbose=self.verbose, log_level=self.log_level)
        search_plan, rinfo, trace = self.stages.searchplan_enhancer.perform(search_step, search_plan)
        if rinfo.status != ReturnStatus.success:
            self.log.warning("Operation ended with error!", verbose=self.verbose, log_level=self.log_level)
            self.log.debug("RESULT:\n* %s\n* %s", rinfo.status, search_plan, verbose=self.verbose, log_level=self.log_level)
        else:
            self.log.debug("Operation ended successfully", verbose=self.verbose, log_level=self.log_level)
            str_searchsteps = '\n'.join(
                [f'{i}. {step}' for i, step in enumerate(search_plan.search_steps)])
            self.log.debug("RESULT:\n%s", str_searchsteps, verbose=self.verbose, log_level=self.log_level)

        return search_plan, rinfo, trace

    @accumulate_stage_info
    def match_searchstep_to_kg(self, search_query: str) -> Tuple[Dict[str, List[VectorDBInstance]], ReturnInfo, CompositeModuleDetailedResult, bool]:
        matched_kg_objects, rinfo, module_trace = None, ReturnInfo(), CompositeModuleDetailedResult()
        self.log.debug("STAGE#2.1.1 - ENTITIES EXTRACTION", verbose=self.verbose, log_level=self.log_level)
        entities, ee_rinfo, trace = self.stages.entities_extractor.perform(search_query)
        module_trace.add("entities_extractor", ModuleType.stage, trace)
        if ee_rinfo.status == ReturnStatus.success:
            self.log.debug("Operation ended successfully", verbose=self.verbose, log_level=self.log_level)
            self.log.debug("RESULT: %s .", entities, verbose=self.verbose, log_level=self.log_level)
        else:
            self.log.warning("Operation ended with error!", verbose=self.verbose, log_level=self.log_level)
        update_rinfo(rinfo, ee_rinfo)

        if rinfo.status == ReturnStatus.success:
            self.log.debug("STAGE#2.1.2 - ENTITIES-TO-KGOBJECTS MATCHING", verbose=self.verbose, log_level=self.log_level)
            matched_kg_objects, e2nm_rinfo, trace = self.stages.entities2nodes_matcher.perform(entities)
            module_trace.add("entities2nodes_matcher", ModuleType.step, trace)
            if e2nm_rinfo.status == ReturnStatus.success:
                self.log.debug("Operation ended successfully", verbose=self.verbose, log_level=self.log_level)
                str_matched_kgobject = '\n'.join([f'- [{entity}][{len(objects)}] ' + ', '.join(list(map(lambda obj: obj.text, objects))) for entity, objects in matched_kg_objects.items()])
                self.log.debug("RESULT:\n%s", str_matched_kgobject, verbose=self.verbose, log_level=self.log_level)
            else:
                self.log.warning("Operation ended with error!", verbose=self.verbose, log_level=self.log_level)
            update_rinfo(rinfo, e2nm_rinfo)
        else:
            self.log.warning("During previous steps error occurs.", verbose=self.verbose, log_level=self.log_level)

        return matched_kg_objects, rinfo, module_trace, False

    def get_cluequeries(self, search_query: str, matched_kg_objects: Dict[str, List[NodeInfo]]) -> Tuple[List[QueryInfo], ReturnInfo, CompositeModuleResult]:
        cluequeries, rinfo, trace = self.stages.cluequeries_generator.perform(search_query, matched_kg_objects)
        str_cluequeries = '\n'.join(
            [f'- {list(map(lambda obj: obj.text, clueq.linked_nodes))}:  {clueq.query}' for clueq in cluequeries])
        if rinfo.status == ReturnStatus.success:
            self.log.debug("Operation ended successfully", verbose=self.verbose, log_level=self.log_level)
            self.log.debug("RESULT: %d\n%s", len(cluequeries), str_cluequeries, verbose=self.verbose, log_level=self.log_level)
        else:
            self.log.warning("Operation ended with error!", verbose=self.verbose, log_level=self.log_level)

        return cluequeries, rinfo, trace

    @accumulate_stage_info
    def search_clueanswers(self, search_query: str, cluequeries: List[QueryInfo]) -> Tuple[List[str], ReturnInfo, CompositeModuleDetailedResult, bool]:
        clueanswers, rinfo, module_trace = [], ReturnInfo(), CompositeModuleDetailedResult()
        for j, cur_cluequery in enumerate(cluequeries):
            self.log.debug("Current clue-query (%d / %d): %s", j, len(cluequeries), cur_cluequery.query, verbose=self.verbose, log_level=self.log_level)
            self.log.debug("Current clue-query hash: %s", create_id(cur_cluequery.query), verbose=self.verbose, log_level=self.log_level)

            self.log.debug("STAGE#3.1.1 - KNOWLEDGE RETRIEVING", verbose=self.verbose, log_level=self.log_level)
            retrieved_triplets, rk_rinfo, trace = self.stages.knowledge_retriever.retrieve(cur_cluequery)
            module_trace.add("knowledge_retriever", ModuleType.stage, trace)
            update_rinfo(rinfo, rk_rinfo)
            if rinfo.status == ReturnStatus.success:
                self.log.debug("Operation ended successfully", verbose=self.verbose, log_level=self.log_level)
                self.log.debug("RESULT: %d", len(retrieved_triplets), verbose=self.verbose, log_level=self.log_level)
                for triplet in retrieved_triplets:
                    self.log.debug("* [%s | %s] %s", triplet.id, triplet.relation.type, TripletCreator.stringify(triplet)[1], verbose=self.verbose, log_level=self.log_level)
            else:
                self.log.warning("Operation ended with error!", verbose=self.verbose, log_level=self.log_level)
                break

            self.log.debug("STAGE#3.1.2 - CLUE-ANSWER GENERATION", verbose=self.verbose, log_level=self.log_level)
            cur_clueanswer, cag_rinfo, trace = self.stages.clueanswer_generator.perform(search_query, retrieved_triplets)
            module_trace.add("clueanswer_generator", ModuleType.stage, trace)
            update_rinfo(rinfo, cag_rinfo)
            if rinfo.status == ReturnStatus.success:
                self.log.debug("Operation ended successfully", verbose=self.verbose, log_level=self.log_level)
                self.log.debug("RESULT: %s", cur_clueanswer, verbose=self.verbose, log_level=self.log_level)
            else:
                self.log.warning("Operation ended with error!", verbose=self.verbose, log_level=self.log_level)
                break

            clueanswers.append(cur_clueanswer)

        return clueanswers, rinfo, module_trace, False

    def summarize_clueanswers(self, search_query: str, cluequeries: List[QueryInfo], clueanswers: List[str]) \
            -> Tuple[str, ReturnInfo, CompositeModuleResult]:
        search_step_answer, rinfo, trace = self.stages.clueanswers_summarizer.perform(
            search_query, list(map(lambda cq_info: cq_info.query, cluequeries)), clueanswers)
        if rinfo.status == ReturnStatus.success:
            self.log.debug("Operation ended successfully", verbose=self.verbose, log_level=self.log_level)
            self.log.debug("RESULT: %s", search_step_answer, verbose=self.verbose, log_level=self.log_level)
        else:
            self.log.warning("Operation ended with error!", verbose=self.verbose, log_level=self.log_level)

        return search_step_answer, rinfo, trace

    def answer_generation_trying(self, search_plan: SearchPlanInfo) -> Tuple[Union[str, None], ReturnInfo, CompositeModuleResult]:
        answer, rinfo, trace = self.stages.answer_generator.perform(search_plan)
        if rinfo.status == ReturnStatus.success:
            self.log.debug("Operation ended successfully", verbose=self.verbose, log_level=self.log_level)
            self.log.debug("RESULT: %s", answer, verbose=self.verbose, log_level=self.log_level)
        else:
            self.log.warning("Operation ended with error!", verbose=self.verbose, log_level=self.log_level)

        return answer, rinfo, trace

    @accumulate_stage_info
    def forced_answer_generation(self, search_plan: SearchPlanInfo) -> Tuple[Union[str, None], ReturnInfo, CompositeModuleDetailedResult, bool]:
        answer, rinfo, module_trace = None, ReturnInfo(), CompositeModuleDetailedResult()
        defined_behaviour = self.config.planlimit_exceeded_behaviour
        if defined_behaviour == PlanLimitExceededBehaviour.strict_answer:
            self.log.debug("Генерируем строгий ответ (с возможностью генерации <|NotEnoughtInfo|> тега) на основе имеющейся информации...", verbose=self.verbose, log_level=self.log_level)
            answer, rinfo.status, trace = self.stages.answer_generator.tasks_solvers.strict_answer_gen_solver.solve(
                lang=self.stages.answer_generator.config.lang, search_plan=search_plan)
            module_trace.add("strictanswer_gen_solver", ModuleType.task_solver, trace)

        elif defined_behaviour == PlanLimitExceededBehaviour.casual_answer:
            self.log.debug("Генерируем нестрогий ответ (без возможности генерации <|NotEnoughtInfo|> тега) на основе имеющейся информации...", verbose=self.verbose, log_level=self.log_level)
            answer, rinfo.status, trace = self.stages.answer_generator.tasks_solvers.casual_answer_gen_solver.solve(
                lang=self.stages.answer_generator.config.lang, search_plan=search_plan)
            module_trace.add("casualanswer_gen_solver", ModuleType.task_solver, trace)

        elif defined_behaviour == PlanLimitExceededBehaviour.noanswer_stub:
            self.log.warning("В рамках заданных ограничений поиска возвращаем <|NotEnoughtInfo|> тег в качестве результата работы.", verbose=self.verbose, log_level=self.log_level)
            answer = "<|NotEnoughtInfo|>"
        else:
            raise ValueError(f"defined_behaviour: {defined_behaviour}")

        if rinfo.status == ReturnStatus.success:
            self.log.debug("Operation ended successfully", verbose=self.verbose, log_level=self.log_level)
        else:
            self.log.warning("Operation ended with error!", verbose=self.verbose, log_level=self.log_level)

        return answer, rinfo, module_trace, False

    @accumulate_stage_info
    def prepare_searchqueries(self, search_query: str, search_step: int) -> Tuple[List[QueryInfo], ReturnInfo, CompositeModuleDetailedResult, bool]:
        cluequeries, rinfo, module_trace = None, ReturnInfo(), CompositeModuleDetailedResult()
        self.log.debug("STAGE#2.1 - SEARCH-STEP to KG MATCHING", verbose=self.verbose, log_level=self.log_level)
        self.log.debug("Current step #%d: %s", search_step, search_query, verbose=self.verbose, log_level=self.log_level)
        matched_kg_objects, ssm_rinfo, trace = self.match_searchstep_to_kg(search_query)
        module_trace.add('match_searchstep_to_kg', ModuleType.stage, trace)
        update_rinfo(rinfo, ssm_rinfo)

        self.log.debug("STAGE#2.2 - CLUE-QUERIES GENERATION", verbose=self.verbose, log_level=self.log_level)
        if rinfo.status == ReturnStatus.success:
            cluequeries, cqg_rinfo, trace = self.get_cluequeries(search_query, matched_kg_objects)
            module_trace.add('get_cluequeries', ModuleType.stage, trace)
            update_rinfo(rinfo, cqg_rinfo)
        else:
            self.log.warning("During previous steps error occurs.", verbose=self.verbose, log_level=self.log_level)

        return cluequeries, rinfo, module_trace, False

    @accumulate_stage_info
    def traverse_kg(self, search_query: str, cluequeries: List[QueryInfo]) -> Tuple[Union[str, None], ReturnInfo, CompositeModuleDetailedResult, bool]:
        search_step_answer, rinfo, module_trace = None, ReturnInfo(), CompositeModuleDetailedResult()
        self.log.debug("STAGE#3.1 - RETRIEVING INFORMATION FROM KG BASED ON CLUE-QUERIES", verbose=self.verbose, log_level=self.log_level)
        clueanswers, cag_rinfo, trace = self.search_clueanswers(search_query, cluequeries)
        module_trace.add("search_clueanswers", ModuleType.stage, trace)
        update_rinfo(rinfo, cag_rinfo)

        self.log.debug("STAGE#3.2 - CLUE-ANSWERS SUMMARISATION", verbose=self.verbose, log_level=self.log_level)
        if rinfo.status == ReturnStatus.success:
            search_step_answer, cas_rinfo, trace = self.summarize_clueanswers(search_query, cluequeries, clueanswers)
            module_trace.add("summarize_clueanswers", ModuleType.stage, trace)
            update_rinfo(rinfo, cas_rinfo)
        else:
            self.log.warning("During previous steps error occurs.", verbose=self.verbose, log_level=self.log_level)

        return search_step_answer, rinfo, module_trace, False

    def get_cache_key(self, query: str) -> List[str]:
        str_using_agent_config = f"{self.using_agent_info['kw']}:{self.using_agent_info['config'].to_str()}"
        return [self.config.to_str(), str_using_agent_config, query]

    @accumulate_stage_info
    @CacheUtils.cache_method_output
    def perform(self, query: str) -> Tuple[str, ReturnInfo, CompositeModuleDetailedResult]:
        """Метод предназначен для выполнения ризонинга на графе знаний с помощью указанного запроса с целью извлечения релевантной информации.

        :param query: запрос на естественном языке.
        :type query: str
        :return: Кортеж из трёх объектов: (1) извлечённая/релевантная информация/ответа на запрос; (2) статус завершения операции с пояснительной информацией; (3) структура данных с промежуточными результатами реботы метода.
        :rtype: Tuple[str, ReturnInfo, CompositeModuleDetailedResult]
        """
        self.log.debug("START MEDIUM KG-REASONING...", verbose=self.verbose, log_level=self.log_level)
        self.log.debug("* Question hash: %s .", create_id(query), verbose=self.verbose, log_level=self.log_level)
        self.log.debug("* Question: %s .", query, verbose=self.verbose, log_level=self.log_level)
        answer, rinfo, module_trace = None, ReturnInfo(), CompositeModuleDetailedResult()
        search_plan = SearchPlanInfo(base_query=query)

        self.log.debug("Start iterative search...", verbose=self.verbose, log_level=self.log_level)
        for search_step in range(self.config.max_searchplan_steps):

            self.log.debug("STAGE#1.1 - SEARCH PLAN INITING/ENHANCING", verbose=self.verbose, log_level=self.log_level)
            search_plan, usp_rinfo, trace = self.update_searchplan(search_step, search_plan)
            module_trace.add("update_searchplan", ModuleType.stage, trace)
            update_rinfo(rinfo, usp_rinfo)

            if rinfo.status == ReturnStatus.success:
                if search_step >= len(search_plan.search_steps):
                    self.log.warning("No more search-steps in the plan!", verbose=self.verbose, log_level=self.log_level)
                    break

            self.log.debug("STAGE#1.2 - SEARCH STEPS RELEVANCE CHECK", verbose=self.verbose, log_level=self.log_level)
            if self.config.enable_searchplan_steps_check:
                if rinfo.status == ReturnStatus.success:
                    if search_step > 0:
                        is_continue_search, rinfo.status, trace = self.stages.searchplan_enhancer.tasks_solvers.searchstop_classify_solver.solve(
                            lang=self.stages.searchplan_enhancer.config.lang, gen_strategy=self.stages.searchplan_enhancer.config.agent_gen_stategy,
                            query=search_plan.base_query, search_steps=search_plan.search_steps, steps_answers=search_plan.steps_answers[:search_step])
                        module_trace.add("searchstop_classify_solver", ModuleType.task_solver, trace)
                    else:
                        is_continue_search = True

                    if rinfo.status == ReturnStatus.success:
                        self.log.debug("Operation ended successfully", verbose=self.verbose, log_level=self.log_level)
                        if not is_continue_search:
                            self.log.warning("RESUTL: Оставшиеся/непройденные шаги плана не позволят найти запрашиваемую/релевантную информацию для текущего/обрабатываемого вопроса.", verbose=self.verbose, log_level=self.log_level)
                            break
                        else:
                            self.log.debug("RESULT: Оставшиеся/непройденные шаги плана успешно прошли проверку на продолжение поиска.", verbose=self.verbose, log_level=self.log_level)
                    else:
                        self.log.warning("Operation ended with error!", verbose=self.verbose, log_level=self.log_level)
                else:
                    self.log.warning("During previous steps error occurs.", verbose=self.verbose, log_level=self.log_level)
                    break
            else:
                self.log.warning("Current stage is disabled. Continue.", verbose=self.verbose, log_level=self.log_level)

            self.log.debug("STAGE#2 - QUERIES PREPARATION FOR KG TRAVERSAL", verbose=self.verbose, log_level=self.log_level)
            if rinfo.status == ReturnStatus.success:
                search_query = search_plan.search_steps[search_step]
                cluequeries, psq_rinfo, trace = self.prepare_searchqueries(search_query, search_step)
                module_trace.add("prepare_searchqueries", ModuleType.stage, trace)
                update_rinfo(rinfo, psq_rinfo)
            else:
                self.log.warning("During previous steps error occurs.", verbose=self.verbose, log_level=self.log_level)
                break

            self.log.debug("STAGE#3 - KG TRAVERSAL FOR RELEVANT KNOWLEDGE EXTRACTION", verbose=self.verbose, log_level=self.log_level)
            if rinfo.status == ReturnStatus.success:
                search_step_answer, tkg_rinfo, trace = self.traverse_kg(search_query, cluequeries)
                module_trace.add("traverse_kg", ModuleType.stage, trace)
                update_rinfo(rinfo, tkg_rinfo)

                if rinfo.status == ReturnStatus.success:
                    search_plan.steps_answers.append(search_step_answer)
            else:
                self.log.warning("During previous steps error occurs.", verbose=self.verbose, log_level=self.log_level)
                break

            self.log.debug("STAGE#4 - ANSWER-GENERATION TRYING", verbose=self.verbose, log_level=self.log_level)
            if rinfo.status == ReturnStatus.success:
                answer, agt_rinfo, trace = self.answer_generation_trying(search_plan)
                module_trace.add("answer_generation_trying", ModuleType.stage, trace)
                update_rinfo(rinfo, agt_rinfo)

                if answer is not None:
                    self.log.debug(ANSWER_IS_GENERATED_MESSAGE, verbose=self.verbose, log_level=self.log_level)
                    break
                else:
                    self.log.debug(CONTINUE_SEARCH_MESSAGE, verbose=self.verbose, log_level=self.log_level)
            else:
                self.log.warning("During previous steps error occurs.", verbose=self.verbose, log_level=self.log_level)
                break

        self.log.debug("Завершаем поиск.", verbose=self.verbose, log_level=self.log_level)
        self.log.debug("Информация по выполненному поиску: %s", search_plan, verbose=self.verbose, log_level=self.log_level)
        if answer is None and rinfo.status == ReturnStatus.success:
            answer, fag_rinfo, trace = self.forced_answer_generation(search_plan)
            module_trace.add("forced_answer_generation", ModuleType.stage, trace)
            update_rinfo(rinfo, fag_rinfo)

        self.log.debug("RETURNED ANSWER: %s", answer, verbose=self.verbose, log_level=self.log_level)
        self.log.debug("STATUS: %s", rinfo.status, verbose=self.verbose, log_level=self.log_level)

        return answer, rinfo, module_trace
