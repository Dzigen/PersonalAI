from .configs import QA_MAIN_LOG_PATH
from .kg_reasoning import KnowledgeGraphReasonerConfig, KnowledgeGraphReasoner
from .query_preprocessing import QueryPreprocessor, QueryPreprocessorConfig
from ...kg_model import KnowledgeGraphModel
from ...utils import Logger, ReturnStatus, ReturnInfo
from ...utils.data_structs import create_id
from ...utils.errors import STATUS_MESSAGE
from ...db_drivers.kv_driver import KeyValueDriverConfig, KVDBConnectionConfig


from dataclasses import dataclass, field
from typing import Tuple, Union

@dataclass
class QAPipelineConfig:
    """

    :param log: Отладочный класс для журналирования/мониторинга поведения инициализируемой компоненты. Значение по умолчанию Logger(LOG_PATH).
    :type log: Logger
    :param verbose: Если True, то информация о поведении класса будет сохраняться в stdout и файл-журналирования (log), иначе только в файл. Значение по умолчанию False.
    :type verbose: bool
    """
    preprocessor_config: QueryPreprocessorConfig = field(default_factory=lambda: QueryPreprocessorConfig())
    reasoner_config: KnowledgeGraphReasonerConfig = field(default_factory=lambda: KnowledgeGraphReasonerConfig())
    aggregator_config: KnowledgeAggregatorConfig = field(default_factory=lambda: KnowledgeAggregatorConfig())

    log: Logger = field(default_factory=lambda: Logger(QA_MAIN_LOG_PATH))
    verbose: bool = False

class QAPipeline:
    """Верхнеуровневый класс QA-конвейера, отвечающий за генерацию ответов на вопросы.

    :param kg_model: Модель памяти (графа знаний) ассистента.
    :type kg_model: KnowledgeGraphModel
    :param config: Конфигурация QA-конвейера. Значение по умолчанию QAPipelineConfig().
    :type config: QAPipelineConfig
    """

    def __init__(self, kg_model: KnowledgeGraphModel, config: QAPipelineConfig = QAPipelineConfig(),
                 cache_kvdriver_config: KeyValueDriverConfig = None) -> None:
        self.config = config
        self.kg_model = kg_model
        self.log = config.log

        self.query_preprocessor = QueryPreprocessor(self.config.preprocessor_config, cache_kvdriver_config)
        self.kg_reasoner = KnowledgeGraphReasoner(kg_model, self.config.reasoner_config, cache_kvdriver_config)
        self.knowledge_aggregator = KnowledgeAggregator(self.config.aggregator_config, cache_kvdriver_config)

    def answer(self, query: str) -> Tuple[str, ReturnInfo]:
        """Метод предназначен для генерации ответа на user-вопрос. Ответ обуславливается на информацию из имеющегося графа знаний.

        :param query: User-вопрос на естественном языке.
        :type query: str
        :return: Кортеж из двух объектов: (1) cгенерированный ответ; (2) статус завершения операции с пояснительной информацией.
        :rtype: Tuple[str, ReturnInfo]
        """
        final_answer, info = None, [], ReturnInfo()

        # Preprocessing stage
        query_info, prepr_info = self.query_preprocessor.perform(query)
        if prepr_info.status != ReturnStatus.success:
            info = prepr_info
        else:
            info.occurred_warning.append(prepr_info.occurred_warning)

        # Reasoning Stage
        if info.status == ReturnStatus.success:
            sub_queries = []
            if query_info.decomposed_query is not None and len(query_info.decomposed_query) > 0:
                sub_queries = query_info.decomposed_query
            elif query_info.enchanced_query is not None:
                sub_queries = [query_info.enchanced_query]
            elif query_info.denoised_query is not None:
                sub_queries = [query_info.denoised_query]
            elif query_info.base_query is not None:
                sub_queries = [query_info.base_query]
            else:
                raise ValueError

            for cur_sub_query in sub_queries:
                cur_sub_answer, reasoner_info = self.kg_reasoner.perform(cur_sub_query)
                if reasoner_info.status != ReturnStatus.success:
                    info.status = reasoner_info.status
                    info.message = reasoner_info.message
                    break

                info.occurred_warning.append(reasoner_info.occurred_warning)     
                query_info.sub_answers.append(cur_sub_answer)
        
        # Answers Aggregation Stage
        if info.status == ReturnStatus.success:
            final_answer, kagg_info = self.knowledge_aggregator.perform(query_info)
            if kagg_info != ReturnStatus.success:
                info.status = kagg_info.status
                info.message = kagg_info.message

        return final_answer, info
