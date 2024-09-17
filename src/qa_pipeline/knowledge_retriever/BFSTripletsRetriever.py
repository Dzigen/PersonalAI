from .utils import AbstractTripletsRetriever
from ...utils.data_structs import QueryInfo, Node, Relation, Triplet
from ...knowledge_graph_model import KnowledgeGraphModel

import copy
from dataclasses import dataclass
from typing import List
import torch

@dataclass
class BFSSearchConfig:
    pass


def process_chain(chain, chain_subj_obj, chain_triplets):
    for triplet in chain:
        subj = triplet[0].items()
        subj = sorted(subj, key=lambda x: x[1])
        obj = triplet[-2].items()
        obj = sorted(obj, key=lambda x: x[1])
        subj = str(subj)
        obj = str(obj)
        rel_props = triplet[2].items()
        rel_props = [(key, value) for key, value in rel_props if key not in ["raw_time", "time"]]
        rel_props = sorted(rel_props, key=lambda x: x[0])
        rel_props = str(rel_props)
        if (subj, obj, rel_props) not in chain_subj_obj and (obj, subj, rel_props) not in chain_subj_obj \
                and triplet not in chain_triplets:
            chain_triplets.append(triplet)
            chain_subj_obj.add((subj, obj, rel_props))
    return chain_subj_obj, chain_triplets


def process_inters_chains1(inters_chains1):
    chain_triplets1 = []
    chain_subj_obj1 = set()
    for chain in inters_chains1:
        chain_subj_obj1, chain_triplets1 = process_chain(chain, chain_subj_obj1, chain_triplets1)
    return chain_triplets1


def process_inters_chains2(inters_chains2):
    chain_triplets2 = []
    chain_subj_obj2 = set()
    for chain1, chain2, *_ in inters_chains2:
        chain_subj_obj2, chain_triplets2 = process_chain(chain1, chain_subj_obj2, chain_triplets2)
        chain_subj_obj2, chain_triplets2 = process_chain(chain2, chain_subj_obj2, chain_triplets2)
    return chain_triplets2


class BFSRetriever(AbstractTripletsRetriever):
    def __init__(self, kg_model: KnowledgeGraphModel, search_config: BFSSearchConfig = None, retriever = None) -> None:
        super().__init__()
        self.kg_model = kg_model
        self.search_config = search_config
        self.retriever = retriever
        self.extract_triplets_name1_template = 'MATCH (a)-[r]-(b) WHERE a.name="{name1}" RETURN a, r, b'
        self.extract_triplets_name2_template = 'MATCH (a)-[r]-(b) WHERE b.name="{name2}" RETURN a, r, b'
        self.extract_triplets_rel_prop_template = 'MATCH (a)-[r]-(b) WHERE r.{prop_name}="{prop_value}" RETURN a, r, b'

    def parse_triplet_output(self, direction, query, another_entities1, another_entities2, chain, subj_labels=None,
                                obj_labels=None, db=None):
        triplets_info = []
        inters_chains1, inters_chains2 = [], []
        try:
            res = self.kg_model.graph_db(query, db=self.config.graphdb_name)
            for element in res:
                rel_props = dict(element["r"])
                rel_props = {key: value for key, value in rel_props.items() if key not in ["raw_time", "sentiment"]}
                if (subj_labels is None or set(element["a"].labels).intersection(set(subj_labels))) \
                        and (obj_labels is None or set(element["b"].labels).intersection(set(obj_labels))):
                    triplet = [{"id": element["a"].element_id,
                                "type": list(element["a"].labels)[0],
                                "name": element["a"]["name"]},
                               {"id": element["r"].element_id,
                                "type": element["r"].type,
                                "prop": rel_props},
                               {"id": element["b"].element_id,
                                "type": list(element["b"].labels)[0],
                                "name": element["b"]["name"]},
                               direction]
                    new_chain = copy.deepcopy(chain)

                    def count_persons(new_chain, second_chain):
                        persons  = set()
                        for cur_chain in [new_chain, second_chain]:
                            for tr in cur_chain:
                                for ent in tr:
                                    if "person" in ent:
                                        persons.add(ent["person"])
                        return persons

                    if triplet not in new_chain:
                        subj = triplet[0]["name"].replace("_", " ")
                        obj = triplet[-2]["name"].replace("_", " ")
                        prop_values = [val.lower() for val in triplet[2]["prop"].values()]
                        cnt1 = 0
                        if subj.lower() in another_entities1:
                            cnt1 += 1 
                        if obj.lower() in another_entities1:
                            cnt1 += 1
                        if any([prop_value.lower() in another_entities1 for prop_value in prop_values]):
                            cnt1 += 1
                        if cnt1 > 0:
                            new_chain.append(triplet)
                            inters_chains1.append([new_chain, cnt1])
                        elif "backw" in direction and subj.lower() in another_entities2:
                            new_chain.append(triplet)
                            second_chain = another_entities2[subj.lower()]
                            persons = count_persons(new_chain, second_chain)
                            if not ([ch[-1] for ch in new_chain] == ["forw", "backw"] \
                                    and [ch[-1] for ch in second_chain] == ["forw", "backw"]) and len(persons) < 3:
                                inters_chains2.append([new_chain, second_chain, ["backw", subj]])
                        elif "forw" in direction and obj.lower() in another_entities2:
                            new_chain.append(triplet)
                            second_chain = another_entities2[obj.lower()]
                            persons = count_persons(new_chain, second_chain)
                            if not ([ch[-1] for ch in new_chain] == ["forw", "backw"] \
                                    and [ch[-1] for ch in second_chain] == ["forw", "backw"]) and len(persons) < 3:
                                inters_chains2.append([new_chain, second_chain, ["forw", obj]])
                        elif any([prop_value.lower() in another_entities2 for prop_value in prop_values]):
                            for prop_value in triplet[2].values():
                                if prop_value.lower() in another_entities2:
                                    new_chain.append(triplet)
                                    second_chain = another_entities2[prop_value.lower()]
                                    persons = count_persons(new_chain, second_chain)
                                    if len(persons) < 3:
                                        inters_chains2.append([new_chain, second_chain, ["prop", prop_value]])
                        else:
                            new_chain.append(triplet)
                    else:
                        new_chain.append(triplet)
                    new_entities = []
                    if "forw" in direction:
                        new_entities.append((element["b"]["name"], "", "node"))
                    if "backw" in direction:
                        new_entities.append((element["a"]["name"], "", "node"))
                    triplets_info.append([triplet, new_entities, new_chain])
        except Exception as e:
            print(f"error in query execution: {e}")
        return triplets_info, inters_chains1, inters_chains2

    def add_chains(self, inters_chains1, inters_chains2, cur_inters_chains1, cur_inters_chains2):
        for ch in cur_inters_chains1:
            if ch not in inters_chains1:
                inters_chains1.append(ch)
        for ch in cur_inters_chains2:
            if ch not in inters_chains2:
                inters_chains2.append(ch)
        return inters_chains1, inters_chains2

    def make_triplet_key(self, triplet):
        subj, rel, obj, *_ = triplet
        rel_data_items = list(rel["prop"].items())
        rel_data_items = [(key.replace("_", " "), value.replace("_", " ")) for key, value in rel_data_items
                          if key not in ["raw_time", "time", "sentiment"]]
        rel_data_items = sorted(rel_data_items, key=lambda x: x[0])
        rel_data_values = [element[1].lower().replace("_", " ") for element in rel_data_items]
        subj_name = [subj["name"].replace("_", " ")]
        obj_name = [obj["name"].replace("_", " ")]
        rel_type = rel["type"].replace("_", " ")
        keys = [subj_name, rel_type, obj_name] + rel_data_values
        keys_rev = [obj_name, rel_type, subj_name] + rel_data_values
        return tuple(keys), tuple(keys_rev)

    def get_relevant_triplets(self, query_info: QueryInfo) -> List[Triplet]:
        seed_entities = []
        for nodes_list in query_info.linked_nodes_by_entities:
            seed_entity = []
            for node in nodes_list:
                seed_entity.append((node.document, "", "node"))
            seed_entities.append(seed_entity)
        triplets_dict, inters_chains1, inters_chains2 = self.bfs(seed_entity, db=self.config.graphdb_name)
        inters_chains1 = sorted(inters_chains1, key=lambda x: x[1], reverse=True)
        inters_chains1_more = [ch for ch, cnt in inters_chains1 if cnt > 1]
        inters_chains1_less = [ch for ch, cnt in inters_chains1 if cnt == 1]
        chain_triplets1_more = process_inters_chains1(inters_chains1_more)
        chain_triplets1_less = process_inters_chains1(inters_chains1_less)
        chain_triplets2 = process_inters_chains2(inters_chains2)
        prob_tr = False
        if inters_chains1_more:
            chain_triplets = chain_triplets1_more + chain_triplets1_less[:3] + chain_triplets2[:3]
            prob_tr = True
        else:
            chain_triplets = chain_triplets1_less + chain_triplets2

        def format_triplet(triplet_data):
            subj, rel, obj, *_ = triplet_data
            subj_node = Node(name=subj["name"], type=subj["type"], id=subj["id"], prop={})
            obj_node = Node(name=obj["name"], type=obj["type"], id=obj["id"], prop={})
            rel_edge = Relation(type=rel["type"], id=rel["id"], prop=rel["prop"])
            triplet = Triplet(start_node=subj_node, relation=rel_edge, end_node=obj_node)
            return triplet

        formatted_triplets = []
        for triplet in chain_triplets[:25]:
            formatted_triplet = format_triplet(triplet)
            formatted_triplets.append(formatted_triplet)

        if chain_triplets:
            thres = 3
        else:
            thres = 6
        if len(chain_triplets) < 20 and not prob_tr:
            total_f_triplets = []
            for (*_, seed_entity, _), triplets in triplets_dict.items():
                f_triplets = []
                for triplet in triplets:
                    reverse_triplet = [triplet[-1]] + triplet[1:-1] + [triplet[0]]
                    if triplet not in total_f_triplets and reverse_triplet not in total_f_triplets:
                        f_triplets.append(triplet)
                        total_f_triplets.append(triplet)
                for triplet in f_triplets[:thres]:
                    formatted_triplet = format_triplet(triplet)
                    formatted_triplets.append(formatted_triplet)
        return formatted_triplets

    def bfs(self, seed_entities, depth=1, subj_labels=None, obj_labels=None, question=None, top_n=10, db=None):
        triplets_dict = {}
        inters_chains1, inters_chains2 = [], []
        # seed_entity, prop_name="", entity_type="node"
        used_entities = {}
        entities = {}
        for step in range(depth):
            for ne, entities_list in enumerate(seed_entities):
                for seed_entity, prop_name, entity_type in entities_list:
                    another_entities_list = [entities_list2 for entities_list2 in seed_entities
                                            if entities_list2 != entities_list]
                    another_entities1, another_entities2 = [], {}
                    for entities_list2 in another_entities_list:
                        for ent, *_ in entities_list2:
                            another_entities1.append(ent.lower())
                    seed_entity = seed_entity.replace(" ", "_").lower()
                    if step == 0:
                        used_entities[(seed_entity, ne)] = set()
                        entities[(seed_entity, ne)] = [(seed_entity, prop_name, entity_type, [])]
                    for (cur_seed_entity, cur_ne), entities_info in entities.items():
                        if cur_ne != ne:
                            for entity, *_, chain in entities_info:
                                if entity.lower() != cur_seed_entity.lower() and entity.lower() != seed_entity.lower() \
                                        and entity not in another_entities1 and entity not in another_entities2:
                                    another_entities2[entity.lower()] = chain

                    triplets_info = []
                    new_entities = []
                    for entity, prop_name, tp, chain in entities[(seed_entity, ne)]:
                        if (entity, prop_name, tp) not in used_entities[(seed_entity, ne)]:
                            if tp == "node":
                                query = self.extract_triplets_name1_template.format(name1=entity)
                                cur_triplets_info, cur_inters_chains1, cur_inters_chains2 = self.parse_triplet_output(
                                    "forw", query, another_entities1, another_entities2, chain, subj_labels, obj_labels, db
                                )
                                inters_chains1, inters_chains2 = \
                                    self.add_chains(inters_chains1, inters_chains2, cur_inters_chains1, cur_inters_chains2)
                                for triplet in cur_triplets_info:
                                    triplets_info.append([(step, "forw", seed_entity, triplet[0][1])] + triplet)
                                query = self.extract_triplets_name2_template.format(name2=entity)
                                cur_triplets_info, cur_inters_chains1, cur_inters_chains2 = self.parse_triplet_output(
                                    "backw", query, another_entities1, another_entities2, chain, subj_labels, obj_labels, db
                                )
                                inters_chains1, inters_chains2 = \
                                    self.add_chains(inters_chains1, inters_chains2, cur_inters_chains1, cur_inters_chains2)
                                for triplet in cur_triplets_info:
                                    triplets_info.append([(step, "backw", seed_entity, triplet[0][1])] + triplet)
                                used_entities[(seed_entity, ne)].add((entity, prop_name, tp))
                            elif tp == "rel_prop":
                                query = self.extract_triplets_rel_prop_template.format(
                                    prop_name=prop_name,
                                    prop_value=entity.capitalize()
                                )
                                cur_triplets_info, cur_inters_chains1, cur_inters_chains2 = self.parse_triplet_output(
                                    "forw/backw", query, another_entities1, another_entities2, chain, subj_labels, obj_labels, db
                                )
                                inters_chains1, inters_chains2 = \
                                    self.add_chains(inters_chains1, inters_chains2, cur_inters_chains1, cur_inters_chains2)
                                for triplet in cur_triplets_info:
                                    triplets_info.append([(step, "forw", seed_entity, triplet[0][1])] + triplet)
                                used_entities[(seed_entity, ne)].add((entity, prop_name, tp))
                    if question and step > 0:
                        triplets_for_rank = [triplet[1] for triplet in triplets_info]
                        cur_embs = []
                        for triplet in triplets_for_rank:
                            triplet_key, triplet_key_rev = self.make_triplet_key(triplet)
                            if triplet_key in self.triplet_embs_dict:
                                emb = self.triplet_embs_dict[triplet_key]
                            else:
                                emb = self.triplet_embs_dict[triplet_key_rev]
                            cur_embs.append(emb)
                        if cur_embs:
                            embs_for_rank = torch.Tensor(cur_embs).to("cuda")
                            query_embs = self.retriever.embed([question])
                            result = self.retriever.search_in_embeds(embs_for_rank, query_embs, 5)
                            idx = result["idx"][0][:top_n]
                            triplets_info = [triplets_info[ind] for ind in idx]

                    for step_dir_seed_rel, triplet, cur_entities, new_chain in triplets_info:
                        for (cur_ent, cur_prop_name, cur_prop_type) in cur_entities:
                            if (cur_ent, cur_prop_name, cur_prop_type, new_chain) not in new_entities:
                                new_entities.append((cur_ent, cur_prop_name, cur_prop_type, new_chain))
                        if step_dir_seed_rel not in triplets_dict:
                            triplets_dict[step_dir_seed_rel] = []
                        triplets_dict[step_dir_seed_rel].append(triplet)
                    entities[(seed_entity, ne)] += new_entities
        return triplets_dict, inters_chains1, inters_chains2