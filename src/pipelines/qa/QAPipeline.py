from dataclasses import dataclass, field
from typing import Tuple, Union, List, Dict
import gc

from .configs import QA_MAIN_LOG_PATH
from .utils import QAPipelineStages
from .kg_reasoning.utils import QueryReasoningInfo
from .kg_reasoning import KnowledgeGraphReasonerConfig, KnowledgeGraphReasoner
from .query_preprocessing import QueryPreprocessor, QueryPreprocessorConfig
from .answers_aggregation import AnswersAggregator, AnswersAggregatorConfig
from ...kg_model import KnowledgeGraphModel
from ...utils import Logger, ReturnStatus, ReturnInfo, update_rinfo
from ...utils.cache_kv import CacheUtils
from ...utils.data_structs import create_id, QueryPreprocessingInfo
from ...db_drivers.kv_driver import KeyValueDriverConfig
from ...utils.cache_kv.CacheOperations import CacheOperations
from ...utils.agent_stat_analyzer.AgentStatOperations import AgentStatOperations
from ...utils.agent_stat_analyzer import AgentStatAnalyzerConfig


@dataclass
class QAPipelineConfig:
    """
    Конфигурация Question-Answering-конвейера.

    :param preprocessor_config: Конфигурация стадии по предобработке исходного user-вопроса. Значение по умолчанию QueryPreprocessorConfig().
    :type preprocessor_config: QueryPreprocessorConfig, optional
    :param reasoner_config: Конфигурация стадии по обходу/ризонингу на графе знаней с целью извлечения релевантой информации к user-вопросу. Значение по умолчанию KnowledgeGraphReasonerConfig().
    :type reasoner_config: KnowledgeGraphReasonerConfig, optional
    :param aggregator_config: Конфигурация стадии по аггрегации/резюмированию информации, полученной в резльтате ризонинга на графе знаний (памяти). Значение по умолчанию AnswersAggregatorConfig().
    :type aggregator_config: AnswersAggregatorConfig, optional
    :param cache_table_name: Название таблицы в структуре (базе) данных, куда будут сохраняться (кешироваться) основные результаты работы QAPipeline-класса. Значение по умолчанию 'qa_pipeline_cache'.
    :type cache_table_name: str, optional
    :param log: Отладочный класс для журналирования/мониторинга поведения инициализируемой компоненты. Значение по умолчанию Logger(QA_MAIN_LOG_PATH).
    :type log: Logger, optional
    :param verbose: Если True, то информация о поведении класса будет сохраняться в stdout и файл-журналирования (log), иначе только в файл. Значение по умолчанию False.
    :type verbose: bool, optional
    """
    preprocessor_config: QueryPreprocessorConfig = field(
        default_factory=lambda: QueryPreprocessorConfig())
    reasoner_config: KnowledgeGraphReasonerConfig = field(
        default_factory=lambda: KnowledgeGraphReasonerConfig())
    aggregator_config: AnswersAggregatorConfig = field(
        default_factory=lambda: AnswersAggregatorConfig())

    cache_table_name: str = 'qa_pipeline_cache'
    log: Logger = field(default_factory=lambda: Logger(QA_MAIN_LOG_PATH))
    verbose: bool = False

    def to_str(self):
        return f"{self.preprocessor_config.to_str()}|{self.reasoner_config.to_str()}|{self.aggregator_config.to_str()}"


class QAPipeline(CacheUtils, CacheOperations, AgentStatOperations):
    """Верхнеуровневый класс QA-конвейера, отвечающий за поиск информации в графе знаний и генерацию ответов на вопросы.

    :param kg_model: Модель памяти (графа знаний) ассистента.
    :type kg_model: KnowledgeGraphModel
    :param config: Конфигурация QA-конвейера. Значение по умолчанию QAPipelineConfig().
    :type config: QAPipelineConfig, optional
    :param cache_kvdriver_config: Конфигурация структуры данных для кеширования промежуточных результатов в рамках компонент данного класса. Значение по умолчению None.
    :type cache_kvdriver_config: Union[KeyValueDriverConfig, None], optional
    :param inferencestat_config: Конфигурация компоненты для сбора информации и расчёта статистик по результатам выполнения inference-операциий в рамках LLM-задач. Значение по умолчанию None.
    :type inferencestat_config: Union[None, AgentStatAnalyzerConfig], optional
    """

    def __init__(self, kg_model: KnowledgeGraphModel, config: QAPipelineConfig = QAPipelineConfig(),
                 cache_kvdriver_config: Union[KeyValueDriverConfig, None] = None,
                 inferencestat_config: Union[None, AgentStatAnalyzerConfig] = None) -> None:

        agent = kg_model.AVAILABLE_AGENTS[kg_model.AGENTS_MAP.qa_pipeline]
        self.using_agent_info = {'kw': agent.CONNECTOR_KW, 'config': agent.config}

        self.stages: QAPipelineStages = QAPipelineStages(
            query_preprocessor=QueryPreprocessor(
                agent, config.preprocessor_config, cache_kvdriver_config, inferencestat_config),
            kg_reasoner=KnowledgeGraphReasoner(
                kg_model, config.reasoner_config, cache_kvdriver_config, inferencestat_config),
            answers_aggregator=AnswersAggregator(
                agent, config.aggregator_config, cache_kvdriver_config, inferencestat_config=inferencestat_config)
        )

        self.cachekv = self.init_cachekv(
            cache_kvdriver_config, config.cache_table_name)

        self.log = config.log
        self.verbose = config.verbose

    def preprocess_query(self, query: str) -> Tuple[QueryPreprocessingInfo, ReturnInfo]:
        query_info, rinfo = self.stages.query_preprocessor.perform(query)
        self.log(f"RESULT: {query_info}", verbose=self.verbose)
        if rinfo.status != ReturnStatus.success:
            self.log("Operation ended with error!", verbose=self.verbose)
        else:
            self.log("Operation ended successfully", verbose=self.verbose)

        return query_info, rinfo

    def process_query(self, query_info: QueryPreprocessingInfo) -> Tuple[QueryReasoningInfo, ReturnInfo]:
        rinfo = ReturnInfo()
        sub_queries, sub_answers = query_info.processed_query, []

        for i, sub_query in enumerate(query_info.processed_query):
            self.log(
                f"Processing sub_query #{i}: {sub_query}", verbose=self.verbose)
            sub_answer, rinfo = self.stages.kg_reasoner.perform(sub_query)
            self.log(f"RESULT: {sub_answer}", verbose=self.verbose)
            if rinfo.status != ReturnStatus.success:
                self.log("Operation ended with error!", verbose=self.verbose)
                rinfo = rinfo
                break
            else:
                self.log("Operation ended successfully", verbose=self.verbose)
                rinfo.occurred_warning.append(rinfo.occurred_warning)
                sub_answers.append(sub_answer)

        str_subqa = "\n".join(
            [f"- [{q}] {a}" for q, a in zip(sub_queries, sub_answers)])
        self.log(f"RESULT:\n{str_subqa}", verbose=self.verbose)
        subq_info = QueryReasoningInfo(
            sub_queries=sub_queries, sub_answers=sub_answers)

        return subq_info, rinfo

    def postprocess_answer(self, query_info: QueryPreprocessingInfo, subq_info: QueryReasoningInfo) -> Tuple[str, ReturnInfo]:
        aggregated_answer, rinfo = self.stages.answers_aggregator.perform(
            query_info, subq_info)
        self.log(f"RESULT: {aggregated_answer}", verbose=self.verbose)
        if rinfo.status != ReturnStatus.success:
            self.log("Operation ended with error!", verbose=self.verbose)
        else:
            self.log("Operation ended successfully", verbose=self.verbose)

        return aggregated_answer, rinfo

    def get_cache_key(self, query: str) -> List[str]:
        str_using_agent_config = f"{self.using_agent_info['kw']}:{self.using_agent_info['config'].to_str()}"
        str_qprep_config = self.stages.query_preprocessor.config.to_str()
        str_qreas_config = self.stages.kg_reasoner.config.to_str()
        str_aaggr_config = self.stages.answers_aggregator.config.to_str()
        return [str_qprep_config, str_qreas_config, str_aaggr_config, str_using_agent_config, query]

    @CacheUtils.cache_method_output
    def answer(self, query: str) -> Tuple[str, ReturnInfo]:
        """Метод предназначен для генерации ответа на user-вопрос. Ответ обуславливается на информацию из имеющегося графа знаний.

        :param query: User-вопрос на естественном языке.
        :type query: str
        :return: Кортеж из двух объектов: (1) cгенерированный ответ; (2) статус завершения операции с пояснительной информацией.
        :rtype: Tuple[str, ReturnInfo]
        """
        self.log("START QA-PIPELINE...", verbose=self.verbose)
        self.log(f"BASE_QUESTION ID: {create_id(query)}", verbose=self.verbose)
        self.log(f"BASE_QUESTION: {query}", verbose=self.verbose)

        final_answer, rinfo = None, ReturnInfo()

        self.log("Preprocessing...", verbose=self.verbose)
        query_info, q_rinfo = self.preprocess_query(query)
        update_rinfo(rinfo, q_rinfo)

        self.log("Reasoning...", verbose=self.verbose)
        if rinfo.status == ReturnStatus.success:
            subq_info, sq_info = self.process_query(query_info)
            update_rinfo(rinfo, sq_info)
        else:
            self.log("During previous steps error occurs.",
                     verbose=self.verbose)

        self.log("Aggregation...", verbose=self.verbose)
        if rinfo.status == ReturnStatus.success:
            final_answer, ag_info = self.postprocess_answer(
                query_info, subq_info)
            update_rinfo(rinfo, ag_info)
        else:
            self.log("During previous steps error occurs.",
                     verbose=self.verbose)

        self.log(f"STATUS: {rinfo.status}", verbose=self.verbose)

        return final_answer, rinfo

    def __del__(self):
        # print("deleting QA-class")
        del self.stages
        gc.collect()
