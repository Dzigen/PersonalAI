from .configs import MEM_UPDATOR_MAIN_LOG_PATH, DEFAULT_REPLACE_SIMPLE_TASK_CONFIG, DEFAULT_REPLACE_THESIS_TASK_CONFIG
from ....utils import Logger, Triplet, AgentTaskSolverConfig, AgentTaskSolver
from ....utils.data_structs import RelationType, NodeType
from ....utils.errors import ReturnInfo, ReturnStatus
from ....agents import AgentDriver, AgentDriverConfig
from ....kg_model import KnowledgeGraphModel

from functools import reduce
from dataclasses import dataclass, field
from typing import Dict, List

@dataclass
class LLMUpdatorConfig:
    """Конфигурация Updator-стадии Memorize-конвейера.

    :param lang: Язык, который будет использоваться в подаваемом на вход тексте. На основании выбранного языка будут использоваться соответствующие промпты для инференса LLM-агента. Если 'auto', то язык определяется автоматически. Значение по умолчанию 'auto'.
    :type lang: str
    :param agent_config: Конфигурация LLM-агента, который будет использоваться в рамках данной стадии.
    :type agent_config: AgentDriverConfig
    :param replace_simple_task_config: Конфигурация атомарной задачи для LLM-агента по поиску устаревших триплетов типа "simple". Значение по умолчанию DEFAULT_REPLACE_SIMPLE_TASK_CONFIG.
    :type replace_simple_task_config: AgentTaskSolverConfig
    :param replace_thesis_task_config: Конфигурация атомарной задачи для LLM-агента по поиску устаревших триплетов типа "hyper". Значение по умолчанию DEFAULT_REPLACE_THESIS_TASK_CONFIG.
    :type replace_thesis_task_config: AgentTaskSolverConfig
    :param log: Отладочный класс для журналирования/мониторинга поведения инициализируемой комопненты. Значение по умолчанию Logger(MEM_UPDATE_LOG).
    :type log: Logger
    :param verbose: Если True, то информация о поведении класса будет сохраняться в stdout и файл-журналирования (log), иначе только в файл. Значение по умолчанию False.
    :type verbose: bool
    """
    lang: str = "auto"
    agent_config: AgentDriverConfig = field(default_factory=lambda: AgentDriverConfig())
    replace_simple_task_config: AgentTaskSolverConfig = field(default_factory=lambda: DEFAULT_REPLACE_SIMPLE_TASK_CONFIG)
    replace_thesis_task_config: AgentTaskSolverConfig = field(default_factory=lambda: DEFAULT_REPLACE_THESIS_TASK_CONFIG)

    log: Logger = field(default_factory=lambda: Logger(MEM_UPDATOR_MAIN_LOG_PATH))
    verbose: bool = False

class LLMUpdator:
    """Верхнеуровневый класс первой стадии Memorize-конвейера для актуализации знаний в памяти ассистента.

    :param kg_model: Модель памяти (графа знаний) ассистента.
    :type kg_model: KnowledgeGraphModel
    :param config: Конфигурация Updator-стадии. Значение по умолчанию LLMUpdatorConfig().
    :type config: LLMUpdatorConfig
    """

    def __init__(self, kg_model: KnowledgeGraphModel,  config: LLMUpdatorConfig) -> None:
        self.config = config
        self.kg_model = kg_model
        self.log = config.log

        self.agent = AgentDriver.connect(config.agent_config)
        self.replace_simple_solver = AgentTaskSolver(self.agent, self.config.replace_simple_task_config)
        self.replace_hyper_solver = AgentTaskSolver(self.agent, self.config.replace_thesis_task_config)

    def find_simple_obsolete_triplet_ids(self, triplets: List[Triplet]) -> List[str]:
        obsolete_triplet_ids = list()
        for base_triplet in triplets:

            # Формируем уникальный список триплетов, которые инциденты вершинам
            # из текущего триплета (если такие вершины присутствуют в графе знаний)
            incident_triplets = dict()
            for base_node in [base_triplet.start_node, base_triplet.end_node]:

                # сопоставляем ноду из триплета нодам в графе знаний по полю name
                matched_nodes = self.kg_model.graph_struct.db_conn.read_by_name(
                    name=base_node.name, type=NodeType.object, object='node')

                for m_node in matched_nodes:
                    neighbour_node_ids = self.kg_model.graph_struct.db_conn.get_adjecent_nodes(m_node.id, [NodeType.object])
                    for neighbour_id in neighbour_node_ids:
                        shared_triplets = self.kg_model.graph_struct.db_conn.get_triplets(m_node.id, neighbour_id)
                        incident_triplets.update({item.id: item for item in shared_triplets})
                incident_triplets = list(incident_triplets.values())

            # Выполняем поиск устаревших триплетов
            tmp_obsolete_triplet_ids, status = self.replace_simple_solver.solve(
                lang=self.config.lang, base_triplet=base_triplet, incident_triplets=incident_triplets)

            if status == ReturnStatus.success:
                obsolete_triplet_ids += tmp_obsolete_triplet_ids

        return obsolete_triplet_ids

    def find_hyper_obsolete_triplet_ids(self, triplets: List[Triplet]) -> List[str]:
        obsolete_triplet_ids = list()
        for base_triplet in triplets:

            # Формируем уникальный список триплетов, которые инциденты вершинам
            # из текущего триплета (если такие вершины присутствуют в графе знаний)
            incident_triplets = dict()

            # сопоставляем ноду из триплета нодам в графе знаний по полю name
            matched_nodes = self.kg_model.graph_struct.db_conn.read_by_name(
                name=base_triplet.start_node.name, type=NodeType.object, object='node')

            for m_node in matched_nodes:
                neighbour_node_ids = self.kg_model.graph_struct.db_conn.get_adjecent_nodes(m_node.id, [NodeType.hyper])
                for neighbour_id in neighbour_node_ids:
                    shared_triplets = self.kg_model.graph_struct.db_conn.get_triplets(m_node.id, neighbour_id)
                    incident_triplets.update({item.id: item for item in shared_triplets})
            incident_triplets = list(incident_triplets.values())

            # Выполняем поиск устаревших триплетов
            tmp_obsolete_triplet_ids, status = self.replace_simple_solver.solve(
                lang=self.config.lang, base_triplet=base_triplet, incident_triplets=incident_triplets)

            if status == ReturnStatus.success:
                obsolete_triplet_ids += tmp_obsolete_triplet_ids

        return obsolete_triplet_ids

    def find_episodic_obsolete_triplet_ids(self, triplets: List[Triplet], obsolete_hyper_triplet_ids: List[str]) -> List[str]:
        obsolete_triplet_ids = list()

        for triplet in triplets:
            # Сопоставляем сущности из триплета вершинам в графе знаний
            matched_object_nodes = self.kg_model.graph_struct.db_conn.read_by_name(
                    name=triplet.start_node.name, type=NodeType.object, object='node')
            matched_episodic_nodes = self.kg_model.graph_struct.db_conn.read_by_name(
                    name=triplet.end_node.name, type=NodeType.episodic, object='node')
            if len(matched_object_nodes) == 0 or len(matched_episodic_nodes) == 0:
                continue

            # Ищем одинаковые hyper-вершины, которые смежны как с текущими object-, так и с episodic-вершинами
            for m_object_n in matched_object_nodes:
                object_adj_hyper_n = self.kg_model.graph_struct.db_conn.get_adjecent_nodes(m_object_n.id, [NodeType.hyper])
                for m_episodic_n in matched_episodic_nodes:
                    object_adj_episodic_n = self.kg_model.graph_struct.db_conn.get_adjecent_nodes(m_episodic_n.id, [NodeType.hyper])

                    shared_hyper_nodes = set(map(lambda item: item.id, object_adj_hyper_n)).intersection(set(map(lambda item: item.id, object_adj_episodic_n)))
                    for shared_hyper_n in shared_hyper_nodes:
                        shared_h_triplets = self.kg_model.graph_struct.db_conn.get_triplets(
                            m_object_n.id, shared_hyper_n.id)
                        assert len(shared_h_triplets) <= 1

                        # Eсли этот триплет в списке на удаление,
                        # то также удаляем эпизодический триплет с данной object-вершиной
                        if shared_h_triplets[0].id in obsolete_hyper_triplet_ids:
                            shared_e_triplets = self.kg_model.graph_struct.db_conn.get_triplets(m_object_n.id, m_episodic_n.id)
                            assert len(shared_e_triplets) <= 1

                            obsolete_triplet_ids.append(shared_e_triplets[0].id)

        return obsolete_triplet_ids

    def get_obsolete_triplet_ids(self, new_triplets: List[Triplet], check_simple: bool = True,
                                 check_hyper: bool = True, check_episodic: bool = True) -> List[str]:
        """Метод предназначен для поиска устаревшей информации в памяти (графе знаний) асситента. Информация представляется в виде набора триплетов.

        :param new_triplets: Список триплетов, на основе которой осуществляется поиск/детекция устаревшей информации в памяти.
        :type new_triplets: List[Triplet]
        :param check_simple: Если True, то будет осуществляться поиск устаревшей информации среди триплетов типа "simple" в графе знаний, иначе False. Значение по умолчанию True.
        :type check_simple: bool, optional
        :param check_hyper: Если True, то будет осуществляться поиск устаревшей информации среди триплетов типа "hyper" в графе знаний, иначе False. Значение по умолчанию True.
        :type check_hyper: bool, optional
        :param check_episodic: Если True, то будет осуществляться поиск устаревшей информации среди триплетов типа "episodic" в графе знаний, иначе False. Значение по умолчанию True.
        :type check_episodic: bool, optional
        :raises ValueError: Данное исключение выбрасывается, если парметр check_episodic == True, а парметр check_hyper == False.
        :return: Список идентификаторов триплетов из графа знаний, в которых содержится устаревшая информация.
        :rtype: List[str]
        """
        obsolete_triplet_ids = {RelationType.simple.value: [], RelationType.hyper.value: [], RelationType.episodic.value: []}

        if check_episodic and not check_hyper:
            raise ValueError

        aggregated_triplets = {RelationType.simple.value: [], RelationType.hyper.value: [], RelationType.episodic.value: []}
        for triplet in new_triplets:
            if triplet.relation.type == RelationType.simple:
                aggregated_triplets[RelationType.simple.value].append(triplet)
            elif triplet.relation.type == RelationType.hyper:
                aggregated_triplets[RelationType.hyper.value].append(triplet)
            elif (triplet.relation.type == RelationType.episodic) and (triplet.start_node.type == NodeType.object):
                aggregated_triplets[RelationType.episodic.value].append(triplet)
            else:
                raise ValueError

        if check_simple:
            obsolete_triplet_ids[RelationType.simple.value] = self.find_simple_obsolete_triplet_ids(
                aggregated_triplets[RelationType.simple.value])
        if check_hyper:
            obsolete_triplet_ids[RelationType.hyper.value] = self.find_hyper_obsolete_triplet_ids(
                aggregated_triplets[RelationType.hyper.value])
        if check_episodic:
            obsolete_triplet_ids[RelationType.episodic.value] = self.find_episodic_obsolete_triplet_ids(
                aggregated_triplets[RelationType.episodic.value], obsolete_triplet_ids[RelationType.hyper.value])

        flatten_triplet_ids = reduce(lambda acc, v: acc + list(v), obsolete_triplet_ids.values(), [])
        return flatten_triplet_ids

    def update_knowledge(self, new_triplets: List[Triplet], delete_obsolete_info:bool=False,
               need_simple:bool=True, need_hyper:bool=True, need_episodic:bool=True) -> ReturnInfo:
        """Метод предназначен для изменения (удаления устаревшей / добавление новой информации) памяти (графа знаний) асситента.

        :param new_triplets: Список триплетов с информацией для добавления в память (граф знаний) асситента.
        :type new_triplets: List[Triplet]
        :param need_simple: Если True, то из входного текста на первой стадии Memorize-конвейера будет выполнено извлечение триплетов с типом связи 'simple', иначе False. Значение по умолчанию True.
        :type need_simple: bool, optional
        :param need_thesises: Если True, то из входного текста на первой стадии Memorize-конвейера будет выполнено извлечение триплетов с типом связи 'hyper', иначе False. Значение по умолчанию True.
        :type need_thesises: bool, optional
        :param need_episodic: Если True, то из входного текста на первой стадии Memorize-конвейера будет выполнено извлечение триплетов с типом связи 'episodic', иначе False. Значение по умолчанию True.
        :type need_episodic: bool, optional
        :param delete_obsolete_info: Если True, то перед добавлением заданной информации будет удалена устаревшая информация из памяти (графа знаний) асситента, инчае False. Значение по умолчанию False.
        :type delete_obsolete_info: bool, optional
        :return: Статус завершения операции с пояснительной информацией.
        :rtype: ReturnInfo
        """
        info = ReturnInfo()

        if delete_obsolete_info:
            self.log(f"Поиск устаревшей информации в памяти ассистента...", verbose=self.config.verbose)
            obsolete_t_ids = self.get_obsolete_triplet_ids(new_triplets, need_simple, need_hyper, need_episodic)
            self.log(f"Результат: суммарное количество устаревших триплетов - {len(obsolete_t_ids)}.", verbose=self.config.verbose)

            self.log(f"Удаление устаревшей информации из памяти асситента...", verbose=self.config.verbose)
            self.kg_model.remove_knowledge(obsolete_t_ids)

        self.log(f"Добавление информации в память асситента...", verbose=self.config.verbose)
        self.kg_model.add_knowledge(new_triplets)

        return info
