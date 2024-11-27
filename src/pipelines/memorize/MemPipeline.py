from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from .configs import MEMORIZE_MAIN_LOG_PATH
from .extractor.LLMExtractor import LLMExtractor
from .updator.LLMUpdator import LLMUpdator
from .extractor import LLMExtractorConfig
from .updator import LLMUpdatorConfig
from ...kg_model import KnowledgeGraphModel
from ...utils import Logger, Triplet, ReturnStatus, ReturnInfo
from ...utils.errors import STATUS_MESSAGE

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

    log: Logger = field(default_factory=lambda: Logger(MEMORIZE_MAIN_LOG_PATH))
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

    def __init__(self, kg_model: KnowledgeGraphModel, config: MemPipelineConfig = MemPipelineConfig()) -> None:
        self.config = config
        self.log = config.log

        self.extractor = LLMExtractor(config.extractor_config)
        self.updator = LLMUpdator(kg_model, config.updator_config)

    def remember(self, text: str, need_simple: bool = True, need_thesises: bool = True, need_episodic: bool = True,
                 delete_obsolete_info: bool = False, properties: Dict = dict()) -> Tuple[List[Triplet], ReturnInfo]:
        """Метод предназначен для извлечения информации (в виде триплетов) из слабоструктурированного текста и обновление/актуализацию знаний в памяти (графе знаний) ассистена.

        :param text: Слабоструктурированный текст на естественном языке.
        :type text: str
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

        # Извлекаем информацию в структурированном формате из текстов на естественном языке
        self.log("="*20, verbose=self.config.verbose)
        self.log("-"*5 + "STAGE#1 - information extraction" + "-"*5, verbose=self.config.verbose)
        new_triplets, info = self.extractor.extract(text, need_simple, need_thesises, need_episodic, properties)
        self.log(f"EXTRACTED INFORMATION FROM TEXT (IN TRIPLET FORMAT): \n{new_triplets}", verbose=self.config.verbose)

        if info.status == ReturnStatus.success:
            self.log("-"*5 + "STAGE#2 - updating information in assistant memory (knowledge graph)" + "-"*5, verbose=self.config.verbose)
            # Добавляем в граф знаний новую информацию; по требванию (delete_obolete_info = True) удаляем устаревшую информацию
            info = self.updator.update_knowledge(new_triplets, delete_obsolete_info)

        self.log("-"*20, verbose=self.config.verbose)
        self.log(f"Статус: {STATUS_MESSAGE[info.status]}", verbose=self.config.verbose)

        return new_triplets, info
