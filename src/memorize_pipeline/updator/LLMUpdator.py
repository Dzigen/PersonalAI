from .utils import MEM_UPDATE_LOG, REPLACE_THESIS_PROMPT, REPLACE_SIMPLE_PROMPT
from ...utils import Logger, Triplet
from ...utils.data_structs import RelationType, NodeType, AgentTaskSuitcase
from ...utils.errors import ReturnInfo, ReturnStatus
from ...agents import AgentDriver, AgentDriverConfig
from ...knowledge_graph_model import KnowledgeGraphModel

from dataclasses import dataclass, field
from typing import Dict, List

@dataclass
class LLMUpdatorConfig:
    """Конфигурация Updator-стадии.

    :param lang: Язык, который будет использоваться в подаваемом на вход тексте. На основании выбранного языка будут использоваться соответствующие промпты. Если 'auto', то язык определяется автоматически. Значение по умолчанию 'auto'.
    :type lang: str
    :param agent_config: Конфигурация LLM-агента, который будет использоваться в рамках данной стадии.
    :type agent_config: AgentDriverConfig
    :param replace_thesis_prompt: Значение по умолчанию REPLACE_THESIS_PROMPT.
    :type replace_thesis_prompt: Dict
    :param replace_simple_prompt: Значение по умолчанию REPLACE_SIMPLE_PROMPT.
    :type replace_simple_prompt: Dict
    :param log: Отладочный класс для журналирования/мониторинга поведения инициализируемой комопненты. Значение по умолчанию Logger(MEM_UPDATE_LOG).
    :type log: Logger
    :param verbose: Если True, то информация о поведении класса будет сохраняться в stdout и файл-журналирования (log), иначе только в файл. Значение по умолчанию False.
    :type verbose: bool
    """
    lang: str = "auto"
    agent_config: AgentDriverConfig = field(default_factory=lambda: AgentDriverConfig)
    replace_simple_task: AgentTaskSuitcase = field(default_factory=lambda: ...)
    replace_thesis_task: AgentTaskSuitcase = field(default_factory=lambda: ...)
    log: Logger = field(default_factory=lambda: Logger(MEM_UPDATE_LOG))
    verbose: bool = False

class LLMUpdator:
    """Верхнеуровневый класс первой стадии Memorize-конвейера для актуализации знаний в памяти ассистента.

    :param config: Конфигурация Updator-стадии. Значение по умолчанию LLMUpdatorConfig().
    :type config: LLMUpdatorConfig
    """

    def __init__(self, kg_model: KnowledgeGraphModel,  config: LLMUpdatorConfig) -> None:
        self.config = config
        self.agent = AgentDriver.connect(config.agent_config)
        self.kg_model = kg_model
        self.log = config.log

    def find_simple_obsolete_triplet_ids(self, triplets: List[Triplet]) -> List[str]:
        obsolete_triplet_ids = list()
        simple_triplets = list(filter(lambda triplet: triplet.relation.type == RelationType.simple, triplets))
        for base_triplet in simple_triplets:

            # Формируем уникальный список триплетов, которые инциденты вершинам
            # из текущего триплета (если такие вершины присутствуют в графе знаний)
            incident_triplets = dict()
            for base_node in [base_triplet.start_node, base_triplet.end_node]:

                # сопоставляем ноду из триплета нодам в графе знаний по полю name
                matched_nodes = self.kg_model.graph_struct.db_conn.read_by_name(
                    name=[base_node.name], type=NodeType.object, object='node')

                for m_node in matched_nodes:
                    neighbour_node_ids = self.kg_model.graph_struct.db_conn.get_adjecent_nodes(m_node.id, [NodeType.object])
                    for neighbour_id in neighbour_node_ids:
                        shared_triplets = self.kg_model.graph_struct.db_conn.get_triplets(m_node.id, neighbour_id)
                        incident_triplets.update({item.id: item for item in shared_triplets})
                incident_triplets = list(incident_triplets.items())

            # Выполняем поиск устаревших триплетов
            obsolete_triplet_ids += self.config.replace_simple_task.solve_task(base_triplet, incident_triplets)
        return obsolete_triplet_ids

    def find_hyper_obsolete_triplet_ids(self, triplets: List[Triplet]) -> List[str]:
        obsolete_triplet_ids = list()
        hyper_triplets = list(filter(lambda triplet: triplet.relation.type == RelationType.hyper, triplets))
        for base_triplet in hyper_triplets:

            # Формируем уникальный список триплетов, которые инциденты вершинам
            # из текущего триплета (если такие вершины присутствуют в графе знаний)
            incident_triplets = dict()

            # сопоставляем ноду из триплета нодам в графе знаний по полю name
            matched_nodes = self.kg_model.graph_struct.db_conn.read_by_name(
                name=[base_triplet.start_node.name], type=NodeType.object, object='node')

            for m_node in matched_nodes:
                neighbour_node_ids = self.kg_model.graph_struct.db_conn.get_adjecent_nodes(m_node.id, [NodeType.hyper])
                for neighbour_id in neighbour_node_ids:
                    shared_triplets = self.kg_model.graph_struct.db_conn.get_triplets(m_node.id, neighbour_id)
                    incident_triplets.update({item.id: item for item in shared_triplets})
            incident_triplets = list(incident_triplets.items())

            # Выполняем поиск устаревших триплетов
            obsolete_triplet_ids += self.config.replace_simple_task.solve_task(base_triplet, incident_triplets)
        return obsolete_triplet_ids

    def find_episodic_obsolete_triplet_ids(triplets: List[Triplet], obsolete_hyper_triplet_ids: List[str]) -> List[str]:
        obsolete_triplet_ids = list()
        episodic_triplets = list(filter(lambda triplet: triplet.relation.type == RelationType.episodic and triplet.start_node.type == NodeType.object, triplets))
        for triplet in episodic_triplets:
            # найти shared hyper-верщина между object и episodic
            # получаем триплет с object- и hyper-вершинами
            # если этот триплет в списке на удаление, то также удаляем эпизодическую связь с данной object-вершиной
            # TODO
            pass

        return obsolete_triplet_ids

    def get_obsolete_triplet_ids(self, new_triplets: List[Triplet], check_simple: bool = True,
                                 check_hyper: bool = True, check_episodic: bool = True) -> List[str]:
        obsolete_triplet_ids = dict()

        if check_episodic and not check_hyper:
            raise ValueError

        if check_simple:
            obsolete_triplet_ids[RelationType.simple.value] = self.find_simple_obsolete_triplet_ids(new_triplets)

        if check_hyper:
            obsolete_triplet_ids[RelationType.hyper.value] = self.find_hyper_obsolete_triplet_ids(new_triplets)

        if check_episodic:
            obsolete_triplet_ids[RelationType.episodic.value] = self.find_episodic_obsolete_triplet_ids(
                new_triplets, obsolete_triplet_ids[RelationType.hyper.value])

        return obsolete_triplet_ids

    def update(self, new_triplets: List[Triplet], delete_obsolete_info:bool=False,
               need_simple:bool=True, need_hyper:bool=True, need_episodic:bool=True) -> ReturnInfo:
        info = ReturnInfo()

        if delete_obsolete_info:
            # Ищём устаревшую информацю в памяти ассистента
            obsolete_t_ids = self.get_obsolete_triplet_ids(new_triplets, need_simple, need_hyper, need_episodic)

            # Удаляем устаревшую информацию из памяти ассистента
            self.kg_model.delete_triplets(obsolete_t_ids)

        # Добавляем новую информацию в память ассистента
        self.kg_model.create_triplets(new_triplets)

        return info


    @staticmethod
    def parse_replacements_simple(raw_replacements):
        raw_replacements = raw_replacements.lower()
        raw_replacements = raw_replacements.split("[[")[-1] if "[[" in raw_replacements else raw_replacements.split("[\n[")[-1]
        pairs = raw_replacements.replace("[", "").strip("]").split("],")
        triplets_to_remove = []
        for pair in pairs:
            splitted_pair = pair.split("->")
            if len(splitted_pair) != 2:
                continue
            first_triplet = splitted_pair[0].split(",")
            if len(first_triplet) != 3:
                continue
            subj, rel, obj = first_triplet[0].strip(''' \n'".,/'''), first_triplet[1].strip(''' \n'".,/'''), first_triplet[2].strip(''' \n'".,/''')
            triplets_to_remove.append(
                [
                    {"name": subj, "type": "remove", "prop": {}},
                    {"name": rel, "prop": {"type": "remove"}},
                    {"name": obj, "type": "remove", "prop": {}}
                ]
            )
        return triplets_to_remove

    @staticmethod
    def parse_replacements_thesis(raw_replacements):
        raw_replacements = raw_replacements.lower()
        predicted_outdated = raw_replacements.split("[")[-1].split("]")[0].split(";")
        predicted_outdated = [pair.strip().split("<-")[1].strip(''' \n'".,/''') for pair in predicted_outdated if "<-" in pair]
        triplets_to_remove = []
        for outdated_thesis in predicted_outdated:
            triplets_to_remove.append(
                [
                    {"name": "remove", "type": "remove", "prop": {}},
                    {"name": "hyper", "prop": {"type": "hyper"}},
                    {"name": outdated_thesis, "type": "hyper", "prop": {}}
                ]
            )
        return triplets_to_remove

    @staticmethod
    def get_entities_from_triplets(triplets):
        entities = []
        for triplet in triplets:
            if triplet[0] not in entities:
                entities.append(triplet[0])
            if triplet[2] not in entities:
                entities.append(triplet[2])
        return entities

    @staticmethod
    def stringify(triplet):
        if triplet[1]["prop"]["type"] in ["hyper", "episodic"]:
            return triplet[1]["prop"]["time"] + ": " + triplet[2]["name"]
        if triplet[1]["prop"]["type"] in ["simple"]:
            return triplet[1]["prop"]["time"] + ": " + " ".join([triplet[0]["name"], triplet[1]["name"], triplet[2]["name"]])

    @staticmethod
    def stringify_all(triplets):
        return list({LLMUpdator.stringify(triplet) for triplet in triplets})
