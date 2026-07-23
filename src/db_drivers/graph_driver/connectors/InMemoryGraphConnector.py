from typing import List, Dict, Union, Set
from collections import defaultdict
from dataclasses import dataclass, field
import gc
from time import time
import pickle
import hashlib
import os

from .configs import DEFAULT_INMEMORYGRAPH_CONFIG
from ..utils import GraphDBConnectionConfig, AbstractGraphDatabaseConnection
from ....utils import Triplet, NodeType
from ....utils.data_structs import RelationType, Node, \
    NodeInfo, RelationInfo, TripletInfo


@dataclass
class InMemoryGraphStructure:
    edges: Dict[str, Set[str]] = field(default_factory=lambda: defaultdict(set))
    adjacent_nodes: Dict[str, Set[str]] = field(default_factory=lambda: defaultdict(set))

    nodes: Dict[str, Node] = field(default_factory=lambda: dict())
    triplets: Dict[str, Triplet] = field(default_factory=lambda: dict())

    typed_strid_relation_index: Dict[str, Set[str]] = field(default_factory=lambda: defaultdict(set))
    typed_strid_node_index: Dict[str, Set[str]] = field(default_factory=lambda: defaultdict(set))

    tid_triplets_index: Dict[str, Set[str]] = field(default_factory=lambda: defaultdict(set))


class InMemoryGraphConnector(AbstractGraphDatabaseConnection):

    def __init__(self, config: Union[Dict, GraphDBConnectionConfig] = DEFAULT_INMEMORYGRAPH_CONFIG) -> None:
        if isinstance(config, dict):
            config = GraphDBConnectionConfig.from_dict(config)
        else:
            config.formate_fields()
        self.config: GraphDBConnectionConfig = config

        self.strcuture: Union[None, InMemoryGraphStructure] = None

    def open_connection(self) -> None:
        if self.config.params['load_from_disk']:
            if self.config.params['load_dump_name'] is None:
                load_path = f"{self.config.params['load_dump_dir']}/{self.config.db_info['db']}/{self.config.db_info['table']}.pkl"
            else:
                load_path = f"{self.config.params['load_dump_dir']}/{self.config.params['load_dump_name']}"
            if os.path.exists(load_path):
                try:
                    with open(load_path, 'rb') as fd:
                        self.strcuture = pickle.load(fd)
                except EOFError:
                    # print(f"The pickle file '{load_path}' is empty or corrupted.")
                    self.strcuture = InMemoryGraphStructure()
            else:
                # print(f"warning: graph-dump '{load_path}' doesnt exists. creating empty graph-store")
                os.makedirs(f"{self.config.params['save_dump_dir']}/{self.config.db_info['db']}", exist_ok=True)
                self.strcuture = InMemoryGraphStructure()
        else:
            os.makedirs(f"{self.config.params['save_dump_dir']}/{self.config.db_info['db']}", exist_ok=True)
            self.strcuture = InMemoryGraphStructure()

        if self.config.need_to_clear:
            self.clear()

    def is_open(self) -> bool:
        need_to_exist = [
            'edges', 'adjacent_nodes', 'nodes', 'relations', 'triplets',
            'typed_strid_node_index', 'str_relation_index', 'tid_triplets_index']
        condition = True
        for field in need_to_exist:
            condition = condition and hasattr(self, field)
        return condition

    def close_connection(self) -> None:
        # print("closing inmemory graph connection...")
        if self.strcuture is None:
            return
        if self.config.params['save_on_disk']:
            save_path = f"{self.config.params['save_dump_dir']}/{self.config.db_info['db']}/{self.config.db_info['table']}"
            if os.path.exists(save_path) and not self.config.params['rewrite']:
                # print("warning: file on that path is already exists")
                postfix = hashlib.md5(str(time.time()).encode()).hexdigest()
                save_path += postfix
            save_path += '.pkl'

            with open(save_path, 'wb') as fd:
                pickle.dump(self.strcuture, fd)

            # print(f"inmemory graph-store saved in: {save_path}")

        self.strcuture = None
        gc.collect()

    def generate_id(self, seed: str = None) -> str:
        return hashlib.md5((str(time()) if seed is None else seed).encode()).hexdigest()

    def create(self, triplets: List[Triplet], creation_info: Dict[int, Dict[str, bool]] = dict()) -> None:
        # triplet-ids checking
        for triplet in triplets:
            if not isinstance(triplet.id, str):
                raise ValueError(f"* bad triplet: {triplet}\n* triplets: {triplets}")
        unique_ids = set(map(lambda triplet: triplet.id, triplets))
        if len(triplets) != len(unique_ids):
            raise ValueError(f"triplets: {triplets}")

        for i, triplet in enumerate(triplets):
            cur_info = creation_info.get(i, None)

            #
            sn_typedid = NodeInfo(id=triplet.start_node.id, type=triplet.start_node.type).to_str()
            if cur_info is None or cur_info['s_node']:
                new_node_id = self.generate_id()
                self.strcuture.typed_strid_node_index[sn_typedid].add(new_node_id)
                self.strcuture.nodes[new_node_id] = triplet.start_node

            en_typedid = NodeInfo(id=triplet.end_node.id, type=triplet.end_node.type).to_str()
            if cur_info is None or cur_info['e_node']:
                new_node_id = self.generate_id()
                self.strcuture.typed_strid_node_index[en_typedid].add(new_node_id)
                self.strcuture.nodes[new_node_id] = triplet.end_node

            sn_ids = list(self.strcuture.typed_strid_node_index[sn_typedid])
            en_ids = list(self.strcuture.typed_strid_node_index[en_typedid])

            # NOTE: если в графе будет несколько вершин с одинаковым str_id,
            # то нам необходимо их все соединить ребром с новой вершиной
            # например:
            # - есть два триплета (n1, rel1, n2) и (n2, rel2, n3) c пустой creation_info (пусть номера это str_id)
            # - сначала стандартно полностью добавляем первый триплет
            # - при добавлении второго триплета у нас вершина n2 в граф добавляется повторно с другим внутренним id (из-за пустого creation_info)
            # - таким образом добавленную в граф вершину n3 нужно связать с вершиной n2 как из второго так и их первого триплетов
            for sn_id in sn_ids:
                for en_id in en_ids:
                    t_id = self.generate_id()
                    self.strcuture.tid_triplets_index[triplet.id].add(t_id)
                    self.strcuture.triplets[t_id] = triplet

                    r_id = self.generate_id()
                    rel_typedid = RelationInfo(id=triplet.relation.id, type=triplet.relation.type).to_str()
                    self.strcuture.typed_strid_relation_index[rel_typedid].add(r_id)

                    self.strcuture.edges[sn_id].add(t_id)
                    self.strcuture.adjacent_nodes[sn_id].add(en_id)

                    self.strcuture.edges[en_id].add(t_id)
                    self.strcuture.adjacent_nodes[en_id].add(sn_id)

    def read(self, ids: List[str]) -> List[Triplet]:
        triplets = []
        for id in ids:
            if not isinstance(id, str):
                raise ValueError(f"* bad id: {id}\n* ids: {ids}")
            t_ids = self.strcuture.tid_triplets_index[id]
            triplets += list(
                map(lambda t_id: self.strcuture.triplets[t_id], list(t_ids)))
        return triplets

    def update(self, items: List[Triplet]) -> None:
        # TODO
        pass

    def delete(self, ids: List[str], delete_info: Dict[int, Dict[str, bool]] = dict()) -> None:
        for id in ids:
            if not isinstance(id, str):
                raise ValueError(f"* bad id: {id}\n* ids: {ids}")

        for i, t_id in enumerate(ids):
            cur_info = delete_info.get(i, None)

            internal_t_ids = self.strcuture.tid_triplets_index[t_id]

            for internal_t_id in internal_t_ids:
                matched_triplet = self.strcuture.triplets[internal_t_id]

                sn_typedid = NodeInfo(id=matched_triplet.start_node.id, type=matched_triplet.start_node.type).to_str()
                internal_snode_ids = list(self.strcuture.typed_strid_node_index[sn_typedid])
                en_typedid = NodeInfo(id=matched_triplet.end_node.id, type=matched_triplet.end_node.type).to_str()
                internal_enode_ids = list(self.strcuture.typed_strid_node_index[en_typedid])

                nodes_id_to_delete = set()
                for sn_id in internal_snode_ids:
                    self.strcuture.edges[sn_id].remove(internal_t_id)
                    self.strcuture.adjacent_nodes[sn_id].difference_update(
                        internal_enode_ids)

                    if (cur_info is None) or cur_info['s_node']:
                        # assert len(self.strcuture.edges[sn_id]) == 0
                        # assert self.strcuture.adjacent_nodes[sn_id] == 0
                        del self.strcuture.nodes[sn_id]
                        nodes_id_to_delete.add(sn_id)

                if ((cur_info is None) or cur_info['s_node']) and len(nodes_id_to_delete):
                    self.strcuture.typed_strid_node_index[sn_typedid].difference_update(nodes_id_to_delete)

                nodes_id_to_delete = set()
                for en_id in internal_enode_ids:
                    self.strcuture.edges[en_id].remove(internal_t_id)
                    self.strcuture.adjacent_nodes[en_id].difference_update(internal_snode_ids)

                    if (cur_info is None) or cur_info['e_node']:
                        # assert len(self.strcuture.edges[en_id]) == 0
                        # assert self.strcuture.adjacent_nodes[en_id] == 0
                        del self.strcuture.nodes[en_id]
                        nodes_id_to_delete.add(en_id)

                if ((cur_info is None) or cur_info['e_node']) and len(nodes_id_to_delete):
                    self.strcuture.typed_strid_node_index[en_typedid].difference_update(nodes_id_to_delete)

                rel_typedid = RelationInfo(id=matched_triplet.relation.id, type=matched_triplet.relation.type).to_str()
                self.strcuture.typed_strid_relation_index[rel_typedid].pop()
                del self.strcuture.triplets[internal_t_id]

            del self.strcuture.tid_triplets_index[t_id]

    def read_by_name(self, name: str, object_type: Union[RelationType, NodeType], object: str = 'relation') -> List[Union[Triplet, Node]]:
        # Note: Реализован наивный способ поиска элементов в графе
        # (алгоритмическая сложность O(n), где n - количество триплетов/вершин в графе)

        if type(object_type) not in [RelationType, NodeType]:
            raise ValueError(f"object_type: {object_type}")

        if not isinstance(name, str):
            raise ValueError(f"name: {name}")

        if len(name) < 1:
            raise ValueError(f"name: {name}")

        if object == 'relation':
            formated_output = [triplet for triplet in self.strcuture.triplets.values(
            ) if triplet.relation.type == object_type and triplet.relation.name == name]
        elif object == 'node':
            formated_output = [node for node in self.strcuture.nodes.values(
            ) if node.type == object_type and node.name == name]
        else:
            raise ValueError(f"object: {object}")

        return formated_output

    def get_adjacent_nodes(self, base_node: NodeInfo,
                           accepted_n_types: List[NodeType] = [NodeType.object, NodeType.hyper, NodeType.episodic, NodeType.time]) -> List[NodeInfo]:
        if not isinstance(base_node.id, str):
            raise ValueError(f"base_node: {base_node}")

        node_ids = self.strcuture.typed_strid_node_index.get(base_node.to_str(), [])
        adjanced_nodes_ids = []
        for node_typedid in node_ids:
            adjanced_nodes_ids += list(self.strcuture.adjacent_nodes[node_typedid])

        filtered_nodes_ids = list(filter(
            lambda n_db_id: self.strcuture.nodes[n_db_id].type in accepted_n_types,
            adjanced_nodes_ids
        ))
        nodes = list(map(
            lambda id: self.strcuture.nodes[id].get_info(),
            filtered_nodes_ids
        ))
        return nodes

    def get_incident_triples(self, base_node: NodeInfo,
                             accepted_n_types: List[NodeType] = [NodeType.object, NodeType.hyper, NodeType.episodic, NodeType.time],
                             accepted_r_types: Union[List[RelationType], None] = None) \
            -> List[TripletInfo]:
        if not isinstance(base_node.id, str):
            raise ValueError(f"base_node: {base_node}")

        node_ids = self.strcuture.typed_strid_node_index.get(base_node.to_str(), [])
        accepted_incident_triples_info = []
        for node_id in node_ids:
            triples_index_ids = list(self.strcuture.edges[node_id])
            for triple_index_id in triples_index_ids:
                cur_triplet = self.strcuture.triplets[triple_index_id]

                if (accepted_r_types is not None) and (cur_triplet.relation.type not in accepted_r_types):
                    continue
                if cur_triplet.start_node.get_typedid() != base_node.to_str():
                    if cur_triplet.start_node.type not in accepted_n_types:
                        continue
                else:
                    if cur_triplet.end_node.type not in accepted_n_types:
                        continue

                accepted_incident_triples_info.append(cur_triplet.get_info())

        return accepted_incident_triples_info

    def get_nodes_shared_ids(self, node1: NodeInfo, node2: NodeInfo, id_type: str = 'both') -> List[Dict[str, str]]:
        if (not isinstance(node1.id, str)) or (not isinstance(node2.id, str)):
            raise ValueError(f"* node1: {node1}\n* node2: {node2}")
        if not isinstance(id_type, str) or id_type not in ['triplet', 'relation', 'both']:
            raise ValueError(f"id_type: {id_type}")

        formated_info = []

        n1_internal_ids = self.strcuture.typed_strid_node_index[node1.to_str()]
        n2_internal_ids = self.strcuture.typed_strid_node_index[node2.to_str()]
        for n1 in n1_internal_ids:
            for n2 in n2_internal_ids:
                shared_internal_tids = self.strcuture.edges[n1].intersection(
                    self.strcuture.edges[n2])

                for internal_tid in shared_internal_tids:
                    if id_type == 'triplet':
                        formated_info.append(
                            {'t_id': self.strcuture.triplets[internal_tid].id})
                    elif id_type == 'relation':
                        formated_info.append(
                            {'r_id': self.strcuture.triplets[internal_tid].relation.id})
                    elif id_type == 'both':
                        formated_info.append({'t_id': self.strcuture.triplets[internal_tid].id,
                                              'r_id': self.strcuture.triplets[internal_tid].relation.id})
                    else:
                        raise ValueError(f"id_type: {id_type}")

        return formated_info

    def get_triplets(self, node1: NodeInfo, node2: NodeInfo) -> List[Triplet]:
        if (not isinstance(node1.id, str)) or (not isinstance(node2.id, str)):
            raise ValueError(f"* node1: {node1}\n* node2: {node2}")

        start_n_db_ids = self.strcuture.typed_strid_node_index[node1.to_str()]
        if len(start_n_db_ids) < 1:
            raise ValueError(f"* node1: {node1}\n* start_n_db_ids: {start_n_db_ids}")
        start_n_edges = set()
        for n_db_id in start_n_db_ids:
            start_n_edges.update(self.strcuture.edges[n_db_id])

        end_n_db_ids = self.strcuture.typed_strid_node_index[node2.to_str()]
        if len(end_n_db_ids) < 1:
            raise ValueError(f"* node2: {node2}\n* end_n_db_ids: {end_n_db_ids}")
        end_n_edges = set()
        for n_db_id in end_n_db_ids:
            end_n_edges.update(self.strcuture.edges[n_db_id])

        shared_triplets_ids = end_n_edges.intersection(start_n_edges)
        triplets = list(map(lambda id: self.strcuture.triplets[id], shared_triplets_ids))
        return triplets

    def get_triplets_by_name(self, subj_names: List[str], obj_names: List[str], obj_type: str) -> List[Triplet]:
        triplets = []
        for triplet in self.strcuture.triplets.values():
            if obj_type in str(triplet.end_node.type):
                if subj_names and triplet.start_node.name in subj_names:
                    triplets.append(triplet)
                elif obj_names and triplet.end_node.name in obj_names:
                    triplets.append(triplet)
        return triplets

    def count_items(self, item_id: Union[None, str, NodeInfo, RelationInfo] = None,
                    id_type: str = None, detailed: bool = False) -> Union[Dict[str, Dict[str, int]], Dict[str, int], int]:
        result = None
        if id_type is None:
            if detailed:
                result = {
                    'triplets': {'simple': 0, 'hyper': 0, 'episodic': 0, 'time': 0},
                    'nodes': {'object': 0, 'hyper': 0, 'episodic': 0, 'time': 0}
                }
                for triplet in self.strcuture.triplets.values():
                    result['triplets'][triplet.relation.type.value] += 1
                for node in self.strcuture.nodes.values():
                    result['nodes'][node.type.value] += 1
            else:
                result = {'triplets': len(self.strcuture.triplets), 'nodes': len(self.strcuture.nodes)}

        elif id_type == 'node':
            result = len(self.strcuture.typed_strid_node_index[item_id.to_str()])

        elif id_type == 'relation':
            result = len(self.strcuture.typed_strid_relation_index[item_id.to_str()])

        elif id_type == 'triplet':
            result = len(self.strcuture.tid_triplets_index[item_id])

        else:
            raise ValueError(f"id_type: {id_type}")

        return result

    def item_exist(self, item_id: Union[str, NodeInfo, RelationInfo], id_type: str = 'triplet') -> bool:
        if not isinstance(item_id, str):
            if type(item_id) in [NodeInfo, RelationInfo]:
                if not isinstance(item_id.id, str):
                    raise ValueError(f"item_id: {item_id}")
            else:
                raise ValueError(f"item_id: {item_id}")

        output = None
        if id_type == 'node':
            output = self.strcuture.typed_strid_node_index[item_id.to_str()]
        elif id_type == 'relation':
            output = self.strcuture.typed_strid_relation_index[item_id.to_str()]
        elif id_type == 'triplet':
            output = self.strcuture.tid_triplets_index[item_id]
        else:
            raise ValueError(f"id_type: {id_type}")

        return len(output) > 0

    def clear(self) -> None:
        del self.strcuture
        self.strcuture = InMemoryGraphStructure()
        gc.collect()
