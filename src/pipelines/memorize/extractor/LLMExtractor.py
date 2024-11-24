from dataclasses import dataclass, field
from typing import List, Dict, Tuple

from ....utils import Logger, ReturnStatus, ReturnInfo, AgentTaskSolver, AgentTaskSolverConfig
from ....utils.errors import MEM_ZERO_EXTRACTED_TRIPLETS_MSG, MEM_BAD_TRIPLET_EXTRACTION_PROMPT_MSG, MEM_BAD_THESIS_EXTRACTION_PROMPT_MSG, NOT_SUPPORTED_LANG_MSG
from ....utils.data_structs import TripletCreator, NodeCreator, Node, Relation, RelationType, NodeType, Triplet
from ....agents import AgentDriver, AgentDriverConfig

from .configs import DEFAULT_EXTRACT_THESISES_TASK_CONFIG, DEFAULT_EXTRACT_TRIPLETS_TASK_CONFIG, MEM_EXTRACTOR_LOG

@dataclass
class LLMExtractorConfig:
    lang: str = "auto"
    agent_config: AgentDriverConfig = field(default_factory=lambda: AgentDriverConfig())
    triplets_extraction_task_config: AgentTaskSolverConfig = field(default_factory=lambda: DEFAULT_EXTRACT_TRIPLETS_TASK_CONFIG)
    thesises_extraction_task_config: AgentTaskSolverConfig = field(default_factory=lambda: DEFAULT_EXTRACT_THESISES_TASK_CONFIG)
    log: Logger = field(default_factory=lambda: Logger(MEM_EXTRACTOR_LOG))
    verbose: bool = False

class LLMExtractor:
    """Верхнеуровневый класс первой стадии Memorize-конвейера для извлечения информации (и её приведения в triplet-формат) из слабоструктурированных данных.

    :param config: Конфигурация Exctrator-стадии. Значение по умолчанию LLMExtractorConfig().
    :type config: LLMExtractorConfig
    """
    def __init__(self, config: LLMExtractorConfig = LLMExtractorConfig()) -> None:
        self.config = config
        self.log = config.log

        self.agent = AgentDriver.connect(config.agent_config)
        self.triplets_extraction_solver = AgentTaskSolver(self.agent, self.config.triplets_extraction_task_config)
        self.thesises_extraction_solver = AgentTaskSolver(self.agent, self.config.thesises_extraction_task_config)


    def extract(self, text: str, need_simple: bool = True, need_thesises: bool = True,
                need_episodic: bool = True, properties: Dict = {}) -> Tuple[List[Triplet], ReturnInfo]:
        """Метод предназначен для извлечения информации (в виде триплетов) из слабоструктурированного текста
        на естественном языке.

        :param text: Слабоструктурированный текст.
        :type text: str
        :param need_simple: Если True, то из входного текста на первой стадии Mem-конвейера будет выполнено извлечение триплетов с типом связи 'simple', иначе False. Значение по умолчанию True.
        :type need_simple: bool, optional
        :param need_thesises: Если True, то из входного текста на первой стадии Mem-конвейера будет выполнено извлечение триплетов с типом связи 'hyper', иначе False. Значение по умолчанию True.
        :type need_thesises: bool, optional
        :param need_episodic: Если True, то из входного текста на первой стадии Mem-конвейера будет выполнено извлечение триплетов с типом связи 'episodic', иначе False. Значение по умолчанию True.
        :type need_episodic: bool, optional
        :param properties: Набор свойств, который должен быть сохранён в памяти вмести с извлечённой из текста информацией, Значение по умолчанию dict().
        :type properties: Dict, optional
        :return: Кортеж из двух объектов: (1) cписок извлечённой из текста информации (в виде триплетов); (2) статус завершения операции с пояснительной информацией.
        :rtype: Tuple[List[Triplet], ReturnInfo]
        """
        assert need_simple or need_thesises
        self.log("START EXTRACTION...", verbose=self.config.verbose)
        new_triplets, info = [], ReturnInfo()

        if need_simple:
            tmp_triplets, status = self.triplets_extraction_solver.solve(lang=self.config.lang, text=text, rel_prop=properties)
            if status == ReturnStatus.bad_format:
                self.log(MEM_BAD_TRIPLET_EXTRACTION_PROMPT_MSG, verbose=self.config.verbose)
                info.occurred_warning.append(status)
            else:
                new_triplets += tmp_triplets

        if need_thesises:
            tmp_triplets, status = self.triplets_extraction_solver.solve(lang=self.config.lang, text=text, node_prop=properties)
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

    @staticmethod
    def get_entities_from_triplets(triplets: List[Triplet]) -> List[Node]:
        entities = {}
        for triplet in triplets:
            entities[triplet.start_node.stringified] = triplet.start_node
            entities[triplet.end_node.stringified] = triplet.end_node
        return list(entities.values())

    @staticmethod
    def get_episodic_relationships(text: str, entities: List[Node], node_prop: Dict = {}, rel_prop: Dict = {}) -> List[Triplet]:
        episodic_node = NodeCreator.create(name=text, n_type=NodeType.episodic, prop={**node_prop})
        episodic_rel = Relation(name=RelationType.episodic.value, type=RelationType.episodic, prop={**rel_prop})
        episodic_triplets = [TripletCreator.create(entity, episodic_rel, episodic_node) for entity in entities]
        return episodic_triplets
