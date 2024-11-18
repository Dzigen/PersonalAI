from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from .utils import MEM_LOG_PATH
from .extractor.LLMExtractor import LLMExtractor
from .updator.LLMUpdator import LLMUpdator
from .extractor import LLMExtractorConfig
from .updator import LLMUpdatorConfig
from ..qa_pipeline.knowledge_retriever.BFSTripletsRetriever import BFSRetriever
from ..knowledge_graph_model import KnowledgeGraphModel
from ..utils import Logger, Triplet, ReturnStatus, ReturnInfo

@dataclass
class MemPipelineConfig:
    """Конфигурация Memorize-конвейера.

    :param extractor_config: Конфигурация первой стадии Memorize-конвейера: извлечение информации из текстовых данных и приведение их в triplet-формат. Значение по умолчанию LLMExtractorConfig().
    :type extractor_config: LLMExtractorConfig
    :param updator_config: Конфигурация второй стадии Mem-конвейера: актуализация знаний в памяти ассистента. Значение по умолчанию LLMUpdatorConfig().
    :type updator_config: LLMUpdatorConfig
    :param log: Отладочный класс для журналирования/мониторинга поведения инициализируемой комопненты. Значение по умолчанию Logger(MEM_LOG_PATH).
    :type log: Logger
    :param verbose: Если True, то информация о поведении класса будет сохраняться в stdout и файл-журналирования (log), иначе только в файл. Значение по умолчанию False.
    :type verbose: bool
    """
    extractor_config: LLMExtractorConfig = field(default_factory=lambda: LLMExtractorConfig())
    updator_config: LLMUpdatorConfig = field(default_factory=lambda: LLMUpdatorConfig())
    log: Logger = field(default_factory=lambda: Logger(MEM_LOG_PATH))
    verbose: bool = False

class MemPipeline:
    """Верхнеуровневый класс Memorize-конвейера, отвечающего за изменение знаний в памяти ассистента.

    :param kg_model: Модель памяти (графа знаний) ассистента.
    :type kg_model: KnowledgeGraphModel
    :param config: Конфигурация Memorize-конвейера. Значение по умолчанию MemPipelineConfig().
    :type config: MemPipelineConfig
    :param bfs: Значение по умолчанию None.
    :type bfs: BFSRetriever
    """

    def __init__(self, kg_model: KnowledgeGraphModel, config: MemPipelineConfig = MemPipelineConfig(), bfs: BFSRetriever = None) -> None:
        self.config = config
        self.log = config.log

        self.extractor = LLMExtractor(config.extractor_config)
        # TODO
        #self.updator = LLMUpdator(config.updator_config, bfs)

        self.kg_model = kg_model

    def remember(self, text: str, replacing_window_width: int = 32, replacing_window_depth: int = 1,
                 need_simple: bool = True, need_thesises: bool = True, need_episodic: bool = True,
                 need_update: bool = False, properties: Dict = dict()) -> Tuple[List[Triplet], ReturnInfo]:
        """Метод предназначен для извлечения информации (в виде триплетов) из слабоструктурированного текста и обновление/актуализацию знаний в памяти (графе знаний) ассистена.

        :param text: Слабоструктурированный текст на естественном языке.
        :type text: str
        :param replacing_window_width: Значение по умолчанию 32.
        :type replacing_window_width: int, optional
        :param replacing_window_depth: Значение по умолчанию 1.
        :type replacing_window_depth: int, optional
        :param need_simple: Если True, то из входного текста на первой стадии Memorize-конвейера будет выполнено извлечение триплетов с типом связи 'simple', иначе False. Значение по умолчанию True.
        :type need_simple: bool, optional
        :param need_thesises: Если True, то из входного текста на первой стадии Memorize-конвейера будет выполнено извлечение триплетов с типом связи 'hyper', иначе False. Значение по умолчанию True.
        :type need_thesises: bool, optional
        :param need_episodic: Если True, то из входного текста на первой стадии Memorize-конвейера будет выполнено извлечение триплетов с типом связи 'episodic', иначе False. Значение по умолчанию True.
        :type need_episodic: bool, optional
        :param need_update: Значение по умолчанию False.
        :type need_update: bool, optional
        :param properties: Набор свойств, который должен быть сохранён в памяти вмести с извлечённой из текста информацией, Значение по умолчанию dict().
        :type properties: Dict, optional
        :return: Кортеж из двух объектов: (1) список с извлечённой из текста информацией (в виде триплетов), который использовался для обновления/актуализации памяти ассистента; (2) статус завершения операции с пояснительной информацией.
        :rtype: Tuple[List[Triplet], ReturnInfo]
        """
        assert need_simple or need_thesises

        new_triplets, info = self.extractor.extract(text, need_simple, need_thesises, need_episodic, properties)
        #self.log("PROCESSED NEW TRIPLETS: " + str(new_triplets), verbose=self.config.verbose)
        if info.status == ReturnStatus.success:
            # TODO
            #if need_update:
            #    triplets_to_remove = self.updator.update(new_triplets, replacing_window_width, replacing_window_depth, need_simple, need_thesises)
            #    self.log("PROCESSED OUTDATED TRIPLETS: " + str(triplets_to_remove))

            # В объекты триплетов добавлются идентикаторы, присвоенные им в рамках графовой бд
            self.kg_model.graph_struct.create_triplets(new_triplets, status_bar=False)
            self.kg_model.embeddings_struct.create_triplets(new_triplets, status_bar=False)

            # TODO
            #if need_update:
            #    ids = self.kg_model.graph_struct.delete_triplets(triplets_to_remove)
            #    triplets_ids = [id[1] for id in ids]
            #    nodes_ids = [id[0] for id in ids] + [id[2] for id in ids]
            #    self.kg_model.graph_struct.delete_triplets(triplets_ids, nodes_ids)

        if info.status != ReturnStatus.success:
            self.log(f"{info.status}: {info.message}", verbose=self.config.verbose)

        return new_triplets, info
