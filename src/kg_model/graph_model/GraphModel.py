from dataclasses import dataclass, field
from typing import List, Dict, Set, Tuple, Union
import math
from tqdm import tqdm
import gc
from copy import deepcopy

from .config import GRAPH_DB_DEFAULT_DRIVER_CONFIG, GRAPH_MODEL_LOG_PATH
from ...db_drivers.graph_driver import GraphDriver, GraphDriverConfig
from ...utils.data_structs import Triplet, RelationType, NodeType, NODES_TYPES_MAP, \
    RELATIONS_TYPES_MAP, BaseComponentConfig
from ...utils import Logger


@dataclass
class GraphModelConfig(BaseComponentConfig):
    """Конфигурация графовой структуры данных.

    :param driver_config: Конфигурация графовой БД. Значение по умолчанию GRAPH_DB_DEFAULT_DRIVER_CONFIG.
    :type driver_config: Union[Dict,GraphDriverConfig], optional
    """
    driver_config: Union[Dict, GraphDriverConfig] = field(default_factory=lambda: GRAPH_DB_DEFAULT_DRIVER_CONFIG)
    log_path: str = GRAPH_MODEL_LOG_PATH

    def to_str(self):
        # TODO
        raise NotImplementedError

    @staticmethod
    def from_dict(dict_config: Dict):
        dictconfig_copy = deepcopy(dict_config)
        formated_config = GraphModelConfig(**dictconfig_copy)
        formated_config.formate_fields()
        return formated_config

    def formate_fields(self):
        if isinstance(self.driver_config, dict):
            self.driver_config = GraphDriverConfig.from_dict(self.driver_config)
        else:
            self.driver_config.formate_fields()


class GraphModel:
    """Структура данных, предназначенная для хранения информации в формате графа.

    :param config: Конфигурация графовой структуры. Значение по умолчанию GraphModelConfig().
    :type config: Union[Dict,GraphModelConfig], optional
    """

    def __init__(self, config: Union[Dict, GraphModelConfig] = GraphModelConfig()) -> None:
        if isinstance(config, dict):
            config: GraphModelConfig = GraphModelConfig.from_dict(config)
        else:
            config.formate_fields()
        self.config = config

        self.db_conn = GraphDriver.connect(self.config.driver_config)

        self.log = Logger(config.log_path)
        self.verbose = self.config.verbose
        self.log_level = self.config.log_level

    def create_triplets(self, triplets: List[Triplet], batch_size: int = 64, status_bar: bool = True) -> Dict[str, Dict[Union[RelationType, NodeType], Set[str]]]:
        """Метод предназначен для сохранения информации, представленной в виде списка триплетов, в графовую структуру.

        :param triplets: Набор триплетов для добавления в графовую структуру.
        :type triplets: List[Triplet]
        :param batch_size: Количество триплетов, которое будет сохраняться за одну create-операцию. Значение по умолчанию 64.
        :type batch_size: int, optional
        :param status_bar: Если True, то во время исполнения операции в stdout будет выводиться статус её исполнения, иначе False. Значение по умолчанию True.
        :type status_bar: bool, optional
        :return: Словарь с информацией о триплетах, которые были добавлены в графовую структуру.
        :rtype: Dict[str, Dict[Union[RelationType, NodeType], Set[str]]]
        """
        self.log.debug("ADDING TRIPLES TO GRAPH-STRUCT...", verbose=self.verbose, log_level=self.log_level)
        def ntype_mapping(): return {n_type: set() for n_type in NODES_TYPES_MAP.values()}
        def reltype_mapping(): return {r_type: set() for r_type in RELATIONS_TYPES_MAP.values()}

        unique_triplet_ids, unique_node_ids = reltype_mapping(), ntype_mapping()
        existed_triplet_ids, existed_node_ids = reltype_mapping(), ntype_mapping()
        created_triplet_ids, created_node_ids = reltype_mapping(), ntype_mapping()

        batches = math.ceil(len(triplets) / batch_size)
        process = tqdm(range(batches)) if status_bar else range(batches)
        for batch_idx in process:
            # if n1 rel n2
            # else empty
            # n1 _ _
            # _ _ n2
            # n1 _ n2
            # _ _ _

            creation_info = dict()
            triplets_to_create = list()
            info_counter = -1
            for triplet_idx in range(batch_idx * batch_size, (batch_idx + 1) * batch_size, 1):
                if triplet_idx >= len(triplets):
                    break

                cur_triplet = triplets[triplet_idx]
                if cur_triplet.id in unique_triplet_ids[cur_triplet.relation.type]:
                    continue
                else:
                    unique_triplet_ids[cur_triplet.relation.type].add(cur_triplet.id)

                if self.db_conn.item_exist(cur_triplet.id, 'triplet'):
                    existed_triplet_ids[cur_triplet.relation.type].add(cur_triplet.id)
                    continue
                else:
                    triplets_to_create.append(cur_triplet)
                    info_counter += 1
                    creation_info[info_counter] = {'s_node': False, 'e_node': False}
                    created_triplet_ids[cur_triplet.relation.type].add(cur_triplet.id)

                sn_id, sn_type = cur_triplet.start_node.id, cur_triplet.start_node.type
                if (sn_id not in unique_node_ids[sn_type]):
                    unique_node_ids[sn_type].add(sn_id)
                    if not self.db_conn.item_exist(cur_triplet.start_node.get_info(), 'node'):
                        creation_info[info_counter]['s_node'] = True
                        created_node_ids[sn_type].add(sn_id)
                    else:
                        existed_node_ids[sn_type].add(sn_id)

                en_id, en_type = cur_triplet.end_node.id, cur_triplet.end_node.type
                if (en_id not in unique_node_ids[en_type]):
                    unique_node_ids[en_type].add(en_id)
                    if not self.db_conn.item_exist(cur_triplet.end_node.get_info(), 'node'):
                        creation_info[info_counter]['e_node'] = True
                        created_node_ids[en_type].add(en_id)
                    else:
                        existed_node_ids[en_type].add(en_id)

            self.db_conn.create(triplets_to_create, creation_info)

        self.log.debug("RESULT:", verbose=self.verbose, log_level=self.log_level)

        utriples_count = {k: len(v) for k, v in unique_triplet_ids.items()}
        etriples_count = {k: len(v) for k, v in existed_triplet_ids.items()}
        self.log.debug("* Triplets info (all): %d .", len(triplets), verbose=self.verbose, log_level=self.log_level)
        self.log.debug("* unique: %s / %s .", utriples_count, unique_triplet_ids, verbose=self.verbose, log_level=self.log_level)
        self.log.debug("* existed: %s / %s .", etriples_count, existed_triplet_ids, verbose=self.verbose, log_level=self.log_level)

        unode_count = {k: len(v) for k, v in unique_node_ids.items()}
        enode_count = {k: len(v) for k, v in existed_node_ids.items()}
        self.log.debug("Nodes info (all): %d .", len(triplets) * 2, verbose=self.verbose, log_level=self.log_level)
        self.log.debug(f"* unique: %s / %s .", unode_count, unique_node_ids, verbose=self.verbose, log_level=self.log_level)
        self.log.debug(f"* existed: %s / %s .", enode_count, existed_node_ids, verbose=self.verbose, log_level=self.log_level)

        return {'triplets': created_triplet_ids, 'nodes': created_node_ids}

    def delete_triplets(self, triplets: List[Triplet], status_bar: bool = False) -> Tuple[Dict[int, Dict[str, bool]], Dict[int, Dict[str, bool]]]:
        """Метод предназначен для удаления информации, представленной в виде списка триплетов, из графовой структуры.

        :param triplets: Набор триплетов на удаление из графовой структуры.
        :type triplets: List[Triplet]
        :param status_bar: Если True, то во время исполнения операции в stdout будет выводиться статус её исполнения, иначе False. Значение по умолчанию True.
        :type status_bar: bool, optional
        :return: Информация для векторной структуры данных, чтобы удалить устаревшие вершины/триплеты и сохранить консистентность памяти ассистента.
        :rtype: Tuple[Dict[int, Dict[str, bool]], Dict[int, Dict[str, bool]]]
        """

        vdb_delete_info, gdb_delete_info = dict(), dict()
        process = tqdm(enumerate(triplets)) if status_bar else enumerate(triplets)
        for i, triplet in process:
            vector_delete_info = {'s_node': False, 'triplet': False, 'e_node': False}
            graph_delete_info = {'s_node': False, 'e_node': False}

            # Если в триплете у стартовой вершины только одно инцидентное ребро,
            # то готовим его к удалению из графовой и векторной структур данных
            s_node_neighbours = self.db_conn.get_adjecent_nodes(triplet.start_node.get_info())
            if len(s_node_neighbours) == 1 and s_node_neighbours[0].to_str() == triplet.end_node.get_typedid():
                graph_delete_info['s_node'] = True
                vector_delete_info['s_node'] = True

            # Если в триплете у конечной вершины только одно инцидентное ребро,
            # то готовим его к удалению из графовой и векторной структур данных
            e_node_neighbours = self.db_conn.get_adjecent_nodes(triplet.end_node.get_info())
            if len(e_node_neighbours) == 1 and e_node_neighbours[0].to_str() == triplet.start_node.get_typedid():
                graph_delete_info['e_node'] = True
                vector_delete_info['e_node'] = True

            # Если в графовой структуре данных содержится только один триплет с таким же строковым представлением (как у текущего triplet),
            # то готовим его к удалению как из графовой, так и из векторной структур данных. Если триплетов с таким же
            # строковым представлением несколько (>=2), то готовим его к удалению только из графовой структуры.
            same_str_id_count = self.db_conn.count_items(triplet.relation.get_info(), id_type='relation')
            if same_str_id_count == 1:
                vector_delete_info['triplet'] = True

            vdb_delete_info[i] = vector_delete_info
            gdb_delete_info[i] = graph_delete_info

            self.db_conn.delete([triplet.id], {0: gdb_delete_info[i]})

        return gdb_delete_info, vdb_delete_info

    def count_items(self, detailed: bool = False) -> Dict[str, int]:
        return self.db_conn.count_items(detailed=detailed)

    def clear(self) -> None:
        """Метод предназначен для удаления содержимого графовой структуры данных."""
        self.db_conn.clear()

    def close_connections(self):
        self.db_conn.close_connection()
