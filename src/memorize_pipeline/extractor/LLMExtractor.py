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
    """_summary_
    """
    #
    lang: str = "auto"
    #
    agent_config: AgentDriverConfig = field(default_factory=lambda: AgentDriverConfig())
    #
    triplet_extract_system_prompt: dict = field(default_factory=lambda: MEM_EXTRACT_TRIPLET_SYSTEM_PROMPT)
    triplet_extract_user_prompt: dict = field(default_factory=lambda: MEM_EXTRACT_TRIPLET_USER_PROMPT)
    triplet_parse_func: dict = field(default_factory=lambda: MEM_TRIPLET_PARSE_FUNC)
    #
    thesis_extract_system_prompt:  dict = field(default_factory=lambda: MEM_EXTRACT_THESIS_SYSTEM_PROMPT)
    thesis_extract_user_prompt: dict = field(default_factory=lambda: MEM_EXTRACT_THESIS_USER_PROMPT)
    thesis_parse_func: dict = field(default_factory=lambda: MEM_THESIS_PARSE_FUNC)
    #
    log: Logger = field(default_factory=lambda: Logger(MEM_EXTRACT_LOG_PATH))
    verbose: bool = False

class LLMExtractor:

    def __init__(self, config: LLMExtractorConfig = LLMExtractorConfig()) -> None:
        """_summary_

        :param config: _description_, defaults to LLMExtractorConfig()
        :type config: LLMExtractorConfig, optional
        """
        self.config = config
        self.agent = AgentDriver.connect(config.agent_config)
        self.log = config.log
        self.num_hyperedges = 0

    def extract(self, text: str, need_simple: bool = True, need_thesises: bool = True,
                need_episodic: bool = True, properties: Dict = {}) -> Tuple[List[Triplet], ReturnInfo]:
        """_summary_

        :param text: _description_
        :type text: str
        :param need_simple: _description_, defaults to True
        :type need_simple: bool, optional
        :param need_thesises: _description_, defaults to True
        :type need_thesises: bool, optional
        :param need_episodic: _description_, defaults to True
        :type need_episodic: bool, optional
        :param properties: _description_, defaults to {}
        :type properties: Dict, optional
        :return: _description_
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
        """_summary_

        :param text: _description_
        :type text: str
        :param lang: _description_
        :type lang: str
        :param node_prop: _description_, defaults to {}
        :type node_prop: dict, optional
        :param rel_prop: _description_, defaults to {}
        :type rel_prop: dict, optional
        :return: _description_
        :rtype: Tuple[List[Triplet], ReturnStatus]
        """
        self.log("TEXT: " + text, verbose=self.config.verbose)
        raw_response = self.agent.generate(
            system_prompt=self.config.triplet_extract_system_prompt[lang],
            user_prompt=self.config.triplet_extract_user_prompt[lang].format(text=text))
        self.log("EXTRACTED TRIPLETS: " + str(raw_response), verbose=self.config.verbose)
        new_triplets, status = self.parse_triplets(raw_response, lang, node_prop, rel_prop)
        return new_triplets, status

    def extract_thesises(self, text: str, lang: str, node_prop: Dict = {}, rel_prop: Dict = {}) -> Tuple[List[Triplet], ReturnStatus]:
        """_summary_

        :param text: _description_
        :type text: str
        :param lang: _description_
        :type lang: str
        :param node_prop: _description_, defaults to {}
        :type node_prop: Dict, optional
        :param rel_prop: _description_, defaults to {}
        :type rel_prop: Dict, optional
        :return: _description_
        :rtype: Tuple[List[Triplet], ReturnStatus]
        """
        self.log("TEXT: " + text, verbose=self.config.verbose)
        raw_response = self.agent.generate(
            system_prompt=self.config.thesis_extract_system_prompt[lang],
            user_prompt=self.config.thesis_extract_user_prompt[lang].format(text=text))
        self.log("EXTRACTED THESISES: " + str(raw_response), verbose=self.config.verbose)
        new_triplets, status = self.parse_thesises(raw_response, lang, node_prop, rel_prop)
        return new_triplets, status

    @staticmethod
    def get_entities_from_triplets(triplets: List[Triplet]) -> List[Node]:
        """_summary_

        :param triplets: _description_
        :type triplets: List[Triplet]
        :return: _description_
        :rtype: List[Node]
        """
        entities = {}
        for triplet in triplets:
            entities[triplet.start_node.stringified] = triplet.start_node
            entities[triplet.end_node.stringified] = triplet.end_node
        return list(entities.values())

    def parse_thesises(self, raw_response: str, lang: str, node_prop: Dict, rel_prop: Dict) -> Tuple[List[Triplet], ReturnStatus]:
        """_summary_

        :param raw_response: _description_
        :type raw_response: str
        :param lang: _description_
        :type lang: str
        :param node_prop: _description_
        :type node_prop: Dict
        :param rel_prop: _description_
        :type rel_prop: Dict
        :return: _description_
        :rtype: Tuple[List[Triplet], ReturnStatus]
        """
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
        """_summary_

        :param raw_response: _description_
        :type raw_response: str
        :param lang: _description_
        :type lang: str
        :param node_prop: _description_
        :type node_prop: Dict
        :param rel_prop: _description_
        :type rel_prop: Dict
        :return: _description_
        :rtype: Tuple[List[Triplet], ReturnStatus]
        """
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
        """_summary_

        :param text: _description_
        :type text: str
        :param entities: _description_
        :type entities: List[Node]
        :param node_prop: _description_, defaults to {}
        :type node_prop: Dict, optional
        :param rel_prop: _description_, defaults to {}
        :type rel_prop: Dict, optional
        :return: _description_
        :rtype: List[Triplet]
        """
        episodic_node = NodeCreator.create(name=text, type=NodeType.episodic, prop={**node_prop})
        episodic_rel = Relation(name=RelationType.episodic.value, type=RelationType.episodic, prop={**rel_prop})
        episodic_triplets = [TripletCreator.create(entity, episodic_rel, episodic_node) for entity in entities]
        return episodic_triplets
