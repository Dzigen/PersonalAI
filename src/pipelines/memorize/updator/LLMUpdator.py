from dataclasses import dataclass, field
from typing import List, Union, Dict, Tuple, Set
from tqdm import tqdm
from copy import deepcopy

from .config import MEM_UPDATOR_MAIN_LOG_PATH
from .utils import MemUpdatorTaskSolvers, MemUpdatorAgentTasksConfig
from ....utils import Logger, Triplet, AgentTaskSolver, accumulate_step_info, accumulate_stage_info, \
    CompositeModuleDetailedResult, ModuleType
from ....utils.data_structs import RelationType, NodeType, create_id, BaseComponentConfig, LanguageConfig
from ....utils.errors import ReturnInfo, ReturnStatus, STATUS_MESSAGE, update_rinfo
from ....kg_model import KnowledgeGraphModel
from ....db_drivers.kv_driver import KeyValueDriverConfig
from ....utils.cache_kv.CacheOperations import CacheOperations
from ....utils.agent_stat_analyzer import AgentStatAnalyzerConfig
from ....utils.agent_stat_analyzer.AgentStatOperations import AgentStatOperations


@dataclass
class LLMUpdatorConfig(BaseComponentConfig, LanguageConfig):
    """Конфигурация Updator-стадии Memorize-конвейера.

    :param agent_gen_stategy: Стратегия генерации текста для используемого LLM-агента. В случае None-значения будет использоваться стратегия по умолчанию. Значение по умолчанию None.
    :type agent_gen_stategy: Union[None, Dict[str, Union[str, int, float]]], optional
    :param agent_tasks_config: Конфигурации LLM-промптов для решения заданных задач с помощью LLM-агента. Значение по умолчанию MemUpdatorAgentTasksConfig().
    :type agent_tasks_config: Union[Dict, MemUpdatorAgentTasksConfig], optional
    :param delete_obsolete_info: Если True, то перед добавлением заданной информации будут удалены устаревшие знания из памяти (графа знаний) ассистента, иначе False. Значение по умолчанию False.
    :type delete_obsolete_info: bool, optional
    """
    agent_gen_stategy: Union[None, Dict[str, Union[str, int, float]]] = None
    agent_tasks_config: Union[Dict, MemUpdatorAgentTasksConfig] = field(default_factory=lambda: MemUpdatorAgentTasksConfig())
    delete_obsolete_info: bool = False

    log: Logger = field(default_factory=lambda: Logger(MEM_UPDATOR_MAIN_LOG_PATH))

    def to_str(self):
        # TODO
        raise NotImplementedError

    @staticmethod
    def from_dict(dict_config: Dict):
        dictconfig_copy = deepcopy(dict_config)
        formated_config = LLMUpdatorConfig(**dictconfig_copy)
        formated_config.formate_fields()
        return formated_config

    def formate_fields(self):
        if isinstance(self.agent_tasks_config, dict):
            self.agent_tasks_config = MemUpdatorAgentTasksConfig.from_dict(self.agent_tasks_config)
        else:
            self.agent_tasks_config.formate_fields()


class LLMUpdator(CacheOperations, AgentStatOperations):
    """Верхнеуровневый класс первой стадии Memorize-конвейера для актуализации знаний в памяти ассистента.

    :param kg_model: Модель памяти (графа знаний) ассистента.
    :type kg_model: KnowledgeGraphModel
    :param config: Конфигурация Updator-стадии. Значение по умолчанию LLMUpdatorConfig().
    :type config: Union[Dict,LLMUpdatorConfig], optional
    :param cache_kvdriver_config: Конфигурация структуры данных для кеширования промежуточных результатов в рамках компонент данного класса. Значение по умолчанию None.
    :type cache_kvdriver_config: Union[KeyValueDriverConfig, None], optional
    :param inferencestat_config: Конфигурация компоненты для сбора информации и расчёта статистик по результатам выполнения inference-операций в рамках LLM-задач. Значение по умолчанию None.
    :type inferencestat_config: Union[None, AgentStatAnalyzerConfig], optional
    """

    def __init__(self, kg_model: KnowledgeGraphModel, config: Union[Dict, LLMUpdatorConfig] = LLMUpdatorConfig(),
                 cache_kvdriver_config: Union[None, KeyValueDriverConfig] = None,
                 inferencestat_config: Union[None, AgentStatAnalyzerConfig] = None) -> None:
        if isinstance(config, dict):
            config: LLMUpdatorConfig = LLMUpdatorConfig.from_dict(config)
        else:
            config.formate_fields()
        self.config = config
        self.config.agent_tasks_config.versions_to_configs()

        self.kg_model = kg_model

        self.tasks_solvers: MemUpdatorTaskSolvers = MemUpdatorTaskSolvers(
            replace_simple_solver=AgentTaskSolver(
                kg_model.AVAILABLE_AGENTS[kg_model.AGENTS_MAP.mem_pipeline],
                self.config.agent_tasks_config.replace_simple, cache_kvdriver_config, inferencestat_config),
            replace_hyper_solver=AgentTaskSolver(
                kg_model.AVAILABLE_AGENTS[kg_model.AGENTS_MAP.mem_pipeline],
                self.config.agent_tasks_config.replace_thesis, cache_kvdriver_config, inferencestat_config)
        )

        self.log = self.config.log
        self.verbose = self.config.verbose

    @accumulate_step_info
    def get_unique_incident_simple_triplets_to_simple_triplet(self, base_triplet: Triplet) -> List[Triplet]:
        incident_triplets: Dict[str, Triplet] = dict()
        for base_node in [base_triplet.start_node, base_triplet.end_node]:

            # сопоставляем ноду из триплета нодам в графе знаний по полю name
            matched_nodes = self.kg_model.graph_struct.db_conn.read_by_name(
                name=base_node.name, object_type=NodeType.object, object='node')

            for m_node in matched_nodes:
                neighbour_nodes = self.kg_model.graph_struct.db_conn.get_adjecent_nodes(
                    m_node.get_info(), [NodeType.object])

                for neighbour_node in neighbour_nodes:
                    shared_triplets = self.kg_model.graph_struct.db_conn.get_triplets(
                        m_node.get_info(), neighbour_node)
                    incident_triplets.update({item.id: item for item in shared_triplets})

        return list(incident_triplets.values())

    @accumulate_stage_info
    def find_simple_obsolete_triplet_ids(self, base_triplet: Triplet) -> Tuple[List[str], ReturnInfo, CompositeModuleDetailedResult]:
        """Метод предназначен для поиска устаревших simple-триплетов в графе знаний по сравнению с указанным (base_triplet) simple-триплетом.

        :param base_triplet: Simple-триплет, на основе которого нужно искать устаревшие simple-триплеты в графе знаний.
        :type base_triplet: Triplet
        :return: Кортеж из трёх объектов: (1) идентификаторы устаревших simple-триплетов; (2) статус завершения операции с пояснительной информацией; (3) структура данных с промежуточными результатами реботы метода.
        :rtype: Tuple[List[str], ReturnInfo, CompositeModuleDetailedResult]
        """
        obsolete_triplet_ids: List[str] = list()
        rinfo, module_trace = ReturnInfo(), CompositeModuleDetailedResult()

        # Формируем список уникальных триплетов, которые инцидентны вершинам
        # из текущего триплета (если такие вершины присутствуют в графе знаний)
        incident_triplets, trace = self.get_unique_incident_simple_triplets_to_simple_triplet(base_triplet)
        module_trace.add("get_unique_incident_simple_triplets_to_simple_triplet", ModuleType.step, trace)

        # Выполняем поиск устаревших триплетов
        tmp_obsolete_triplet_ids, status, trace = self.tasks_solvers.replace_simple_solver.solve(
            lang=self.config.lang, gen_strategy=self.config.agent_gen_stategy,
            base_triplet=base_triplet, incident_triplets=incident_triplets)
        module_trace.add("replace_simple_solver", ModuleType.task_solver, trace)

        if status == ReturnStatus.success:
            obsolete_triplet_ids += tmp_obsolete_triplet_ids
        rinfo.status = status

        return list(set(obsolete_triplet_ids)), rinfo, module_trace

    @accumulate_step_info
    def get_unique_incident_hyper_triplets_to_hyper_triplet(self, base_triplet: Triplet) -> List[Triplet]:
        incident_triplets: Dict[str, Triplet] = dict()

        # сопоставляем ноду из триплета нодам в графе знаний по полю name
        matched_nodes = self.kg_model.graph_struct.db_conn.read_by_name(
            name=base_triplet.start_node.name, object_type=NodeType.object, object='node')

        for m_node in matched_nodes:
            neighbour_nodes = self.kg_model.graph_struct.db_conn.get_adjecent_nodes(
                m_node.get_info(), [NodeType.hyper])

            for neighbour_node in neighbour_nodes:
                shared_triplets = self.kg_model.graph_struct.db_conn.get_triplets(
                    m_node.get_info(), neighbour_node)

                incident_triplets.update({item.id: item for item in shared_triplets})

        return list(incident_triplets.values())

    @accumulate_stage_info
    def find_hyper_obsolete_triplet_ids(self, base_triplet: Triplet) -> Tuple[List[str], ReturnInfo, CompositeModuleDetailedResult]:
        """Метод предназначен для поиска устаревших hyper-триплетов в графе знаний по сравнению с указанным (base_triplet) hyper-триплетом.

        :param base_triplet: Hyper-триплет, на основе которого нужно искать устаревшие hyper-триплеты в графе знаний.
        :type base_triplet: Triplet
        :return: Кортеж из трёх объектов: (1) идентификаторы устаревших hyper-триплетов; (2) статус завершения операции с пояснительной информацией; (3) структура данных с промежуточными результатами реботы метода.
        :rtype: Tuple[List[str], ReturnInfo, CompositeModuleDetailedResult]
        """
        obsolete_triplet_ids: List[str] = list()
        rinfo, module_trace = ReturnInfo(), CompositeModuleDetailedResult()

        # Формируем список уникальных триплетов, которые инцидентны вершинам
        # из текущего триплета (если такие вершины присутствуют в графе знаний)
        incident_triplets, trace = self.get_unique_incident_hyper_triplets_to_hyper_triplet(base_triplet)
        module_trace.add('get_unique_incident_hyper_triplets_to_hyper_triplet', ModuleType.step, trace)

        # Выполняем поиск устаревших триплетов
        tmp_obsolete_triplet_ids, status, trace = self.tasks_solvers.replace_hyper_solver.solve(
            lang=self.config.lang, gen_strategy=self.config.agent_gen_stategy,
            base_triplet=base_triplet, incident_triplets=incident_triplets)
        module_trace.add('replace_hyper_solver', ModuleType.task_solver, trace)

        if status == ReturnStatus.success:
            obsolete_triplet_ids += tmp_obsolete_triplet_ids
        rinfo.status = status

        return list(set(obsolete_triplet_ids)), rinfo, module_trace

    @accumulate_step_info
    def find_episodic_o_obsolete_triplet_ids(self, base_triplet: Triplet) -> List[str]:
        """Метод предназначен для поиска устаревших episodic-триплетов (с object-вершиной) в графе знаний по сравнению с указанным (base_triplet) episodic-триплетом.

        :param base_triplet: Episodic-триплет (с object-вершиной), на основе которого нужно искать устаревшие episodic-триплеты в графе знаний.
        :type base_triplet: Triplet
        :return: Идентификаторы устаревших episodic-триплетов.
        :rtype: List[str]
        """
        obsolete_triplet_ids = list()

        # Сопоставляем object-сущность из триплета вершинам в графе знаний
        matched_object_nodes = self.kg_model.graph_struct.db_conn.read_by_name(
            name=base_triplet.start_node.name, object_type=NodeType.object, object='node')

        if len(matched_object_nodes) == 0:
            return obsolete_triplet_ids

        for m_object_n in matched_object_nodes:
            # Для object-вершины ищем смежные episodic-вершины
            object_adj_episodic = self.kg_model.graph_struct.db_conn.get_adjecent_nodes(
                m_object_n.get_info(), [NodeType.episodic])

            if len(object_adj_episodic) < 1:
                continue

            # Для object-вершины ищем смежные hyper-вершины
            object_adj_hyper_typedids = set(map(
                lambda node_info: node_info.to_str(),
                self.kg_model.graph_struct.db_conn.get_adjecent_nodes(m_object_n.get_info(), [NodeType.hyper])
            ))

            for episodic_node in object_adj_episodic:
                # Для episodic-вершины, смежной с текущей object-вершиной, ищем смежные hyper-вершины
                episodic_adj_hyper_typedids = set(map(
                    lambda node_info: node_info.to_str(),
                    self.kg_model.graph_struct.db_conn.get_adjecent_nodes(episodic_node, [NodeType.hyper])
                ))

                shared_hyper_ids = object_adj_hyper_typedids.intersection(episodic_adj_hyper_typedids)
                if len(shared_hyper_ids) < 1:
                    # Если у данных object-вершины и episodic-вершины нет общей hyper-вершины, значит данный episodic-триплет устарел
                    # и его нужно добавить в список на удаление
                    episodic_triplet = self.kg_model.graph_struct.db_conn.get_triplets(m_object_n.get_info(), episodic_node)
                    assert len(episodic_triplet) == 1

                    obsolete_triplet_ids.append(episodic_triplet[0].id)

        return list(set(obsolete_triplet_ids))

    @accumulate_step_info
    def find_episodic_h_obsolete_triplet_ids(self, base_triplet: Triplet) -> List[str]:
        """Метод предназначен для поиска устаревших episodic-триплетов (c hyper-вершиной) в графе знаний по сравнению с указанным (base_triplet) episodic-триплетом.

        :param base_triplet: Episodic-триплет (с hyper-вершиной), на основе которого нужно искать устаревшие episodic-триплеты в графе знаний.
        :type base_triplet: Triplet
        :return: Идентификаторы устаревших episodic-триплетов.
        :rtype: List[str]
        """
        obsolete_triplet_ids = list()

        # Сопоставляем hyper-сущность из триплета вершинам в графе знаний
        matched_hyper_nodes = self.kg_model.graph_struct.db_conn.read_by_name(
            name=base_triplet.start_node.name, object_type=NodeType.hyper, object='node')

        if len(matched_hyper_nodes) == 0:
            return obsolete_triplet_ids

        for m_hyper_n in matched_hyper_nodes:

            # Проверям: с каким количеством object-вершин смежна данная hyper-вершина
            hyper_adj_object = self.kg_model.graph_struct.db_conn.get_adjecent_nodes(m_hyper_n.get_info(), [NodeType.object])
            if len(hyper_adj_object) < 1:
                # Если у hyper-вершины нет смежных object-вершин, то связи со всеми episodic-вершинами являются устаревшими
                hyper_adj_episodic = self.kg_model.graph_struct.db_conn.get_adjecent_nodes(m_hyper_n.get_info(), [NodeType.episodic])
                for episodic_node in hyper_adj_episodic:
                    episodic_triplets = self.kg_model.graph_struct.db_conn.get_triplets(m_hyper_n.get_info(), episodic_node)
                    assert len(episodic_triplets) == 1
                    obsolete_triplet_ids.append(episodic_triplets[0].id)

        return list(set(obsolete_triplet_ids))

    @accumulate_stage_info
    def update_knowledge(self, new_triplets: List[Triplet], status_bar: bool = False) \
            -> Tuple[Tuple[Dict[str, Dict[int, Dict[str, bool]]], Dict[str, Dict[str, Set[str]]]], ReturnInfo, CompositeModuleDetailedResult]:
        """Метод предназначен для изменения (удаления устаревшей / добавление новой информации) памяти (графа знаний) ассистента.

        :param new_triplets: Список триплетов с информацией для добавления в память (граф знаний) ассистента.
        :type new_triplets: List[Triplet]
        :param status_bar: Если True, то в stdout будет записываться прогресс выполнения операции, иначе False. Значение по умолчанию False.
        :type status_bar: bool, optional
        :return: Кортеж из трёх объектов: (1) кортеж с информацией о триплетах, удалённых их графа знаний в рамках операции по поиску устаревшей информации и триплетах, добавленных в граф; (2) статус завершения операции с пояснительной информацией; (3) структура данных с промежуточными результатами реботы метода.
        :rtype: Tuple[Tuple[Dict[str, Dict[int, Dict[str, bool]]], Dict[str, Dict[str, Set[str]]]], ReturnInfo, CompositeModuleDetailedResult]
        """

        self.log("START KNOWLEDGE UPDATING...", verbose=self.verbose)
        self.log(f"TRIPLETS_ID: {create_id(f'{new_triplets}')}", verbose=self.verbose)
        rinfo, module_trace = ReturnInfo(), CompositeModuleDetailedResult()

        if self.config.delete_obsolete_info:
            obsolete_triplets_counter = 0

            self.log(f"START SEARCH OF OBSOLETE TRIPLETS IN MEMORY...", verbose=self.verbose)
            # Note: обрабатываем каждый триплет по отдельности, так как в пуле триплетов могут быть такие,
            # которые заменяют одни и те же устаревшие триплеты. Соответственно, мы должны итеративно обновлять память и сохранить
            # только последнюю актуальную информацию.
            process = tqdm(new_triplets) if status_bar else new_triplets
            for triplet in process:
                self.log(f"BASE_TRIPLET ID: {triplet.id}", verbose=self.verbose)
                self.log(f"BASE_TRIPLET: {triplet}", verbose=self.verbose)

                if triplet.relation.type == RelationType.simple:
                    obsolete_t_ids, findost_rinfo, trace = self.find_simple_obsolete_triplet_ids(triplet)
                    module_trace.add('find_simple_obsolete_triplet_ids', ModuleType.stage, trace)
                    update_rinfo(rinfo, findost_rinfo)

                elif triplet.relation.type == RelationType.hyper:
                    obsolete_t_ids, findoht_rinfo, trace = self.find_hyper_obsolete_triplet_ids(triplet)
                    module_trace.add('find_hyper_obsolete_triplet_ids', ModuleType.stage, trace)
                    update_rinfo(rinfo, findoht_rinfo)

                elif (triplet.relation.type == RelationType.episodic) and (triplet.start_node.type == NodeType.object):
                    obsolete_t_ids, trace = self.find_episodic_o_obsolete_triplet_ids(triplet)
                    module_trace.add('find_episodic_o_obsolete_triplet_ids', ModuleType.step, trace)

                elif (triplet.relation.type == RelationType.episodic) and (triplet.start_node.type == NodeType.hyper):
                    obsolete_t_ids, trace = self.find_episodic_h_obsolete_triplet_ids(triplet)
                    module_trace.add('find_episodic_h_obsolete_triplet_ids', ModuleType.step, trace)

                else:
                    raise ValueError

                self.log("RESULT:", verbose=self.verbose)
                self.log(f"* OBSOLETE TRIPELTS AMOUNT - {len(obsolete_t_ids)}", verbose=self.verbose)
                self.log(f"* OBSOLETE TRIPLET IDS - {obsolete_t_ids}", verbose=self.verbose)
                obsolete_triplets_counter += len(obsolete_t_ids)

                self.log(f"DELETING OBSOLETE TRIPLETS FROM MEMORY...", verbose=self.verbose)
                obsolete_triplets = self.kg_model.graph_struct.db_conn.read(obsolete_t_ids)
                self.log(f"TRIPLETS TO DELETE: {len(obsolete_triplets)}", verbose=self.verbose)
                for obs_t in obsolete_triplets:
                    self.log(f"* [{obs_t.id}] {obs_t}", verbose=self.verbose)
                remove_info, trace = self.kg_model.remove_knowledge(obsolete_triplets)
                module_trace.add('remove_knowledge', ModuleType.step, trace)
                self.log(f"REMOVE INFO: {remove_info}", verbose=self.verbose)

                self.log(f"ADDING NEW TRIPLET TO MEMORY...", verbose=self.verbose)
                add_info, trace = self.kg_model.add_knowledge([triplet])
                module_trace.add('add_knowledge', ModuleType.step, trace)
                self.log(f"ADD INFO: {add_info}", verbose=self.verbose)

            self.log(f"FINAL RESULT:", verbose=self.verbose)
            self.log(f"- SUM AMOUNT OF OBSOLETE TRIPELTS: {obsolete_triplets_counter}", verbose=self.verbose)

        else:
            self.log(f"ADDING TRIPLETS TO MEMORY...", verbose=self.verbose)
            add_info, trace = self.kg_model.add_knowledge(new_triplets, status_bar=status_bar)
            module_trace.add('add_knowledge', ModuleType.step, trace)
            self.log(f"ADD INFO: {add_info}", verbose=self.verbose)

        return (remove_info, add_info), rinfo, module_trace
