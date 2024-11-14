from dataclasses import dataclass, field
from typing import List, Dict, Tuple
import ast

from .utils import MEM_EXTRACT_LOG_PATH, MEM_EXTRACT_TRIPLET_SYSTEM_PROMPT, MEM_EXTRACT_TRIPLET_USER_PROMPT, \
    MEM_EXTRACT_THESIS_SYSTEM_PROMPT, MEM_EXTRACT_THESIS_USER_PROMPT, \
    MEM_TRIPLET_PARSE_FUNC, MEM_THESIS_PARSE_FUNC

from ...utils import Logger, detect_lang, ReturnStatus, ReturnInfo
from ...utils.errors import MEM_ZERO_EXTRACTED_TRIPLETS_MSG, MEM_BAD_TRIPLET_EXTRACTION_PROMPT_MSG, MEM_BAD_THESIS_EXTRACTION_PROMPT_MSG, NOT_SUPPORTED_LANG_MSG
from ...utils.data_structs import TripletCreator, NodeCreator, Node, Relation, RelationType, NodeType, Triplet
from ...agents import AgentDriver, AgentDriverConfig

@dataclass
class LLMExtractorConfig:
    #: Язык, который будет использоваться в подаваемом на вход тексте.
    #: На основании выбранного языка будут использоваться соответствующие промпты.
    #: Если 'auto', то язык определяется автоматически.
    lang: str = "auto"
    #: Конфигурация LLM-агента, который будет использоваться в рамках данной стадии
    agent_config: AgentDriverConfig = field(default_factory=lambda: AgentDriverConfig())
    #: Промпты и parse-функция для LLM-агента, которые используются для извлечения триплетов типа "simple" их входного текста
    triplet_extract_system_prompt: dict = field(default_factory=lambda: MEM_EXTRACT_TRIPLET_SYSTEM_PROMPT)
    #: TODO
    triplet_extract_user_prompt: dict = field(default_factory=lambda: MEM_EXTRACT_TRIPLET_USER_PROMPT)
    #: TODO
    triplet_parse_func: dict = field(default_factory=lambda: MEM_TRIPLET_PARSE_FUNC)
    #: Промпты и parse-функция для LLM-агента, которые используются для извлечения триплетов типа "hyper" их входного текста
    thesis_extract_system_prompt:  dict = field(default_factory=lambda: MEM_EXTRACT_THESIS_SYSTEM_PROMPT)
    #: TODO
    thesis_extract_user_prompt: dict = field(default_factory=lambda: MEM_EXTRACT_THESIS_USER_PROMPT)
    #: TODO
    thesis_parse_func: dict = field(default_factory=lambda: MEM_THESIS_PARSE_FUNC)
    #: Отладочный класс для журналирования/мониторинга поведения комопненты.
    log: Logger = field(default_factory=lambda: Logger(MEM_EXTRACT_LOG_PATH))
    #: Если, True, то информация о поведении класса будет сохраняться в stdout и файл-журналирования (log), иначе только в файл.
    verbose: bool = False

class LLMExtractor:
    """Верхнеуровневый класс первой стадии Mem-конвейера
    для извлечения информации (и её приведения в triplet-формат) из слабоструктурированных данных."""
    def __init__(self, config: LLMExtractorConfig = LLMExtractorConfig()) -> None:
        self.config = config
        self.agent = AgentDriver.connect(config.agent_config)
        self.log = config.log
        self.num_hyperedges = 0

    def extract(self, text: str, need_simple: bool = True, need_thesises: bool = True,
                need_episodic: bool = True, properties: Dict = {}) -> Tuple[List[Triplet], ReturnInfo]:
        """Метод предназначен для извлечения информации (в виде триплетов) из слабоструктурированного текста
        на естественном языке.

        :param text: Слабоструктурированный текст.
        :type text: str
        :param need_simple: Если True, то из входного текста на первой стадии Mem-конвейера будет выполнено извлечение триплетов с типом связи 'simple', иначе False, defaults to True
        :type need_simple: bool, optional
        :param need_thesises: Если True, то из входного текста на первой стадии Mem-конвейера будет выполнено извлечение триплетов с типом связи 'hyper', иначе False, defaults to True
        :type need_thesises: bool, optional
        :param need_episodic: Если True, то из входного текста на первой стадии Mem-конвейера будет выполнено извлечение триплетов с типом связи 'episodic', иначе False, defaults to True
        :type need_episodic: bool, optional
        :param properties: Набор свойств, который должен быть сохранён в памяти вмести с извлечённой из текста информацией, defaults to dict()
        :type properties: Dict, optional
        :return: Кортеж из двух объектов: (1) cписок извлечённой из текста информации (в виде триплетов); (2) статус завершения операции с пояснительной информацией.
        :rtype: Tuple[List[Triplet], ReturnInfo]
        """
        assert need_simple or need_thesises
        self.log("START EXTRACTION...", verbose=self.config.verbose)
        new_triplets, info = [], ReturnInfo()
        detected_lang, status = detect_lang(text) if self.config.lang == 'auto' else (self.config.lang, ReturnStatus.success)
        self.log(f"DETECTED LANG: {detected_lang}", verbose=self.config.verbose)
        if status == ReturnStatus.not_supported_lang:
            self.log(NOT_SUPPORTED_LANG_MSG, verbose=self.config.verbose)
            info.occurred_warning.append(status)

        if status == ReturnStatus.success:
            if need_simple:
                tmp_triplets, status = self.extract_triplets(text, detected_lang, rel_prop=properties)
                if status == ReturnStatus.bad_format:
                    self.log(MEM_BAD_TRIPLET_EXTRACTION_PROMPT_MSG, verbose=self.config.verbose)
                    info.occurred_warning.append(status)
                else:
                    new_triplets += tmp_triplets

            if need_thesises:
                tmp_triplets, status = self.extract_thesises(text, detected_lang, node_prop=properties)
                if status == ReturnStatus.bad_format:
                    self.log(MEM_BAD_THESIS_EXTRACTION_PROMPT_MSG, verbose=self.config.verbose)
                    info.occurred_warning.append(status)
                else:
                    new_triplets += tmp_triplets

            if need_episodic:
                new_triplets += self.get_episodic_relationships(
                    text, self.get_entities_from_triplets(new_triplets), node_prop=properties)

        if len(new_triplets) == 0:
            info.status = ReturnStatus.zero_triplets
            info.message = MEM_ZERO_EXTRACTED_TRIPLETS_MSG

        return new_triplets, info

    def extract_triplets(self, text: str, lang: str, node_prop = {}, rel_prop = {}) -> Tuple[List[Triplet], ReturnStatus]:
        self.log("TEXT: " + text, verbose=self.config.verbose)
        raw_response = self.agent.generate(
            system_prompt=self.config.triplet_extract_system_prompt[lang],
            user_prompt=self.config.triplet_extract_user_prompt[lang].format(text=text))
        self.log("EXTRACTED TRIPLETS: " + str(raw_response), verbose=self.config.verbose)
        new_triplets, status = self.parse_triplets(raw_response, lang, node_prop, rel_prop)
        return new_triplets, status

    def extract_thesises(self, text: str, lang: str, node_prop: Dict = {}, rel_prop: Dict = {}) -> Tuple[List[Triplet], ReturnStatus]:
        self.log("TEXT: " + text, verbose=self.config.verbose)
        raw_response = self.agent.generate(
            system_prompt=self.config.thesis_extract_system_prompt[lang],
            user_prompt=self.config.thesis_extract_user_prompt[lang].format(text=text))
        self.log("EXTRACTED THESISES: " + str(raw_response), verbose=self.config.verbose)
        new_triplets, status = self.parse_thesises(raw_response, lang, node_prop, rel_prop)
        return new_triplets, status

    @staticmethod
    def get_entities_from_triplets(triplets: List[Triplet]) -> List[Node]:
        entities = {}
        for triplet in triplets:
            entities[triplet.start_node.stringified] = triplet.start_node
            entities[triplet.end_node.stringified] = triplet.end_node
        return list(entities.values())

    def parse_thesises(self, raw_response: str, lang: str, node_prop: Dict, rel_prop: Dict) -> Tuple[List[Triplet], ReturnStatus]:
        raw_triplets, status = self.config.thesis_parse_func[lang](raw_response)
        formated_triplets = []
        for triplet in raw_triplets:
            thesis, entities = triplet

            thesis_node = NodeCreator.create(name=str(thesis), type=NodeType.hyper, prop={**node_prop})
            thesis_rel = Relation(name=RelationType.hyper.value, type=RelationType.hyper, prop={**rel_prop})
            for entity in entities:
                formated_triplets.append(TripletCreator.create(
                    NodeCreator.create(name=str(entity), type=NodeType.object, prop={**node_prop}),
                    thesis_rel, thesis_node))

        return formated_triplets, status

    def parse_triplets(self, raw_response: str, lang: str, node_prop: Dict, rel_prop: Dict) -> Tuple[List[Triplet], ReturnStatus]:
        raw_triplets, status = self.config.triplet_parse_func[lang](raw_response)
        formated_triplets = []
        for triplet in raw_triplets:
            subj, rel, obj = triplet
            formated_triplets.append(TripletCreator.create(
                NodeCreator.create(name=str(subj), type=NodeType.object, prop={**node_prop}),
                Relation(name=str(rel), type=RelationType.simple, prop={**rel_prop}),
                NodeCreator.create(name=str(obj), type=NodeType.object, prop={**node_prop})))

        return formated_triplets, status

    @staticmethod
    def get_episodic_relationships(text: str, entities: List[Node], node_prop: Dict = {}, rel_prop: Dict = {}) -> List[Triplet]:
        episodic_node = NodeCreator.create(name=text, type=NodeType.episodic, prop={**node_prop})
        episodic_rel = Relation(name=RelationType.episodic.value, type=RelationType.episodic, prop={**rel_prop})
        episodic_triplets = [TripletCreator.create(entity, episodic_rel, episodic_node) for entity in entities]
        return episodic_triplets
