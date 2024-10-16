import copy
from dataclasses import dataclass
from typing import List

import torch

from ...knowledge_graph_model import KnowledgeGraphModel
from ...utils.data_structs import QueryInfo, NodeCreator, Relation, TripletCreator, Triplet, Node, RELATIONS_TYPES_MAP
from .utils import AbstractTripletsRetriever


@dataclass
class BFSSearchConfig:
    graphdb_name: str = "diaasq2"


def process_chain(chain, chain_subj_obj, chain_triplets):
    for triplet in chain:
        subj = triplet[0]
        subj_no_props = {key: value for key, value in subj.items() if key != "prop"}
        subj_props = subj["prop"]
        subj = list(subj_no_props.items()) + list(subj_props.items())
        subj = sorted(subj, key=lambda x: x[1])
        obj = triplet[2]
        obj_no_props = {key: value for key, value in obj.items() if key != "prop"}
        obj_props = obj["prop"]
        obj = list(obj_no_props.items()) + list(obj_props.items())
        obj = sorted(obj, key=lambda x: x[1])
        subj = str(subj)
        obj = str(obj)
        rel_props = triplet[1]["prop"].items()
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
    def __init__(self,
                 kg_model: KnowledgeGraphModel,
                 log=None,
                 search_config: BFSSearchConfig = None,
                 cache=None,
                 verbose=None,
                 retriever=None
                ) -> None:
        super().__init__()
        self.kg_model = kg_model
        self.config = search_config
        self.retriever = retriever
        self.extract_triplets_name1_template = \
            'MATCH (a:object)-[r]-(b:object) WHERE a.name="{name1}" RETURN a, r, b'
        self.extract_triplets_name2_template = \
            'MATCH (a:object)-[r]-(b:object) WHERE b.name="{name2}" RETURN a, r, b'
        self.extract_triplets_rel_prop_template = \
            'MATCH (a:object)-[r]-(b:object) WHERE r.{prop_name}="{prop_value}" RETURN a, r, b'

    def parse_triplet_output(self, direction, query, another_entities1, another_entities2, chain):
        triplets_info = []
        inters_chains1, inters_chains2 = [], []
        try:
            subj_name, obj_name, obj_type = query
            res = self.kg_model.graph_struct.db_conn.get_triplets_by_name(subj_name, obj_name, obj_type)
            for triplet_raw in res:
                triplet = [{"id": triplet_raw.start_node.id,
                            "type": triplet_raw.start_node.type,
                            "name": triplet_raw.start_node.name.replace("_", " "),
                            "prop": triplet_raw.start_node.prop},
                            {"id": triplet_raw.relation.id,
                            "type": triplet_raw.relation.type,
                            "prop": triplet_raw.relation.prop},
                            {"id": triplet_raw.end_node.id,
                            "type": triplet_raw.end_node.type,
                            "name": triplet_raw.end_node.name.replace("_", " "),
                            "prop": triplet_raw.end_node.prop},
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
                    prop_values = [val.lower() for val in triplet[1]["prop"].values()]
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
                        for prop_value in triplet[1]["prop"].values():
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
                    new_entities.append((triplet_raw.end_node.name, "", "node"))
                if "backw" in direction:
                    new_entities.append((triplet_raw.start_node.name, "", "node"))
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

    def get_relevant_triplets(self, query_info: QueryInfo, depth: int = 1) -> List[Triplet]:
        seed_entities = []
        if hasattr(query_info, "entities_with_types"):
            entities_with_types = query_info.entities_with_types
            entity_types = list(entities_with_types.values())
            same_types = len(entity_types) > 1 and all([entity_type == entity_types[0]
                                                        for entity_type in entity_types])
        else:
            same_types = False

        for nodes_list in query_info.linked_nodes_by_entities:
            seed_entity = []
            for node in nodes_list:
                if isinstance(node, str):
                    seed_entity.append((node, "", "node"))
                else:
                    seed_entity.append((node.document, "", "node"))
            seed_entities.append(seed_entity)

        triplets_dict, inters_chains1, inters_chains2 = self.bfs(seed_entities, depth)
        output_texts = self.extract_thesis(seed_entities, same_types)

        thres = 25
        if len(inters_chains1) == 1:
            thres = 25
        elif len(inters_chains1) == 2:
            thres = 12
        elif len(inters_chains1) >= 3:
            thres = 10

        chain_triplets = []
        for seed_entity in inters_chains1:
            ent_chain_triplets = []
            ent_inters_chains1 = inters_chains1[seed_entity]
            ent_inters_chains2 = inters_chains2[seed_entity]
            ent_inters_chains1 = sorted(ent_inters_chains1, key=lambda x: x[1], reverse=True)

            inters_chains1_more = [ch for ch, cnt in ent_inters_chains1 if cnt > 1]
            inters_chains1_less = [ch for ch, cnt in ent_inters_chains1 if cnt == 1]
            chain_triplets1_more = process_inters_chains1(inters_chains1_more)
            chain_triplets1_less = process_inters_chains1(inters_chains1_less)

            chain_triplets2 = process_inters_chains2(ent_inters_chains2)
            prob_tr = False
            if inters_chains1_more:
                #chain_triplets = chain_triplets1_more + chain_triplets1_less[:3] + chain_triplets2[:3]
                ent_chain_triplets = chain_triplets1_more
                prob_tr = True
            else:
                ent_chain_triplets = chain_triplets1_less + chain_triplets2
            chain_triplets += ent_chain_triplets[:thres]

        def format_triplet(triplet_data):
            subj, rel, obj, *_ = triplet_data
            subj_node = NodeCreator.create(name=subj["name"], type=subj["type"], id=subj["id"], prop=subj["prop"])
            obj_node = NodeCreator.create(name=obj["name"], type=obj["type"], id=obj["id"], prop=obj["prop"])
            rel_edge = Relation(name="", type=RELATIONS_TYPES_MAP[rel["type"]], id=rel["id"], prop=rel["prop"])
            triplet = TripletCreator.create(start_node=subj_node, relation=rel_edge, end_node=obj_node, add_stringified_triplet=False)
            return triplet

        def triplet_from_hyper(text, seed_entity, obj_props, rel_props):
            subj_node = NodeCreator.create(name=seed_entity, type="object", id="1", prop={})
            obj_node = NodeCreator.create(name=text, type="hyper", id="1", prop=obj_props)
            rel_edge = Relation(name="", type=RELATIONS_TYPES_MAP["hyper"], id="1", prop=rel_props)
            triplet = TripletCreator.create(start_node=subj_node, relation=rel_edge, end_node=obj_node, add_stringified_triplet=False)
            return triplet

        ex_triplets = []
        formatted_triplets = []
        for text, seed_entity, obj_props, rel_props in output_texts:
            triplet = triplet_from_hyper(text, seed_entity, obj_props, rel_props)
            formatted_triplets.append(triplet)

        for triplet in chain_triplets:
            subj, rel, obj, *_ = triplet
            if (subj, rel, obj) not in ex_triplets and (obj, rel, subj) not in ex_triplets:
                formatted_triplet = format_triplet(triplet)
                formatted_triplets.append(formatted_triplet)
                ex_triplets.append((subj, rel, obj))

        if chain_triplets:
            thres = 3
        else:
            thres = 6

        if not chain_triplets and not prob_tr and not output_texts:
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


    def extract_thesis_for_entities(self, seed_entities, entities_list, entity_type, texts_set):
        cur_texts = []
        for seed_entity, *_ in entities_list:
            another_entities_list = [entities_list2 for entities_list2 in seed_entities
                                        if entities_list2 != entities_list]
            res1 = self.kg_model.graph_struct.db_conn.get_triplets_by_name(seed_entity, None, entity_type)
            res2 = self.kg_model.graph_struct.db_conn.get_triplets_by_name(seed_entity.lower(), None, entity_type)

            for element in res1 + res2:
                obj_dict = element.end_node.prop
                rel_dict = element.relation.prop
                text = element.end_node.name.strip()
                obj_props = {key: value for key, value in obj_dict.items() if key != "name"}
                text_chunks = text.split("\n")
                for text_chunk in text_chunks:
                    text_chunk = text_chunk.strip()
                    if text_chunk not in texts_set:
                        num_inters = 0
                        for entities_list2 in another_entities_list:
                            found = False
                            for ent, *_ in entities_list2:
                                if ent.lower() in text_chunk.lower() \
                                        or ent.lower() in obj_props.values() \
                                        or ent.lower() in rel_dict.values():
                                    found = True
                            if found:
                                num_inters += 1
                        cur_texts.append([text_chunk, seed_entity, obj_props, rel_dict, num_inters])
                        texts_set.add(text_chunk)
        return cur_texts, texts_set


    def extract_thesis(self, seed_entities, same_types):
        output_texts = []
        retr_texts = {ne: [] for ne in range(len(seed_entities))}
        texts_set = set()
        for ne, entities_list in enumerate(seed_entities):
            cur_texts1, texts_set = self.extract_thesis_for_entities(seed_entities, entities_list, "hyper", texts_set)
            cur_texts2, texts_set = self.extract_thesis_for_entities(seed_entities, entities_list, "episodic", texts_set)
            retr_texts[ne] = cur_texts1 + cur_texts2

        for key in retr_texts:
            retr_texts[key] = sorted(retr_texts[key], key=lambda x: x[-1], reverse=True)

        if len(seed_entities) == 1:
            thres = 15
        elif len(seed_entities) == 2:
            thres = 10
        else:
            thres = 7
        print("extract_thesis, thres", thres)

        if same_types:
            for key in retr_texts:
                cur_texts = [[text, seed_entity, obj_props, rel_props]
                             for text, seed_entity, obj_props, rel_props, _ in retr_texts[key]]
                output_texts += cur_texts[:thres]
        else:
            for key in retr_texts:
                cur_texts = [[text, seed_entity, obj_props, rel_props]
                             for text, seed_entity, obj_props, rel_props, cnt in retr_texts[key] if cnt > 0]
                output_texts += cur_texts[:thres]
        return output_texts


    def bfs(self, seed_entities, depth=1, subj_labels=None, obj_labels=None, question=None, top_n=10,
            insert_underscores=False, use_rel_props=False):
        triplets_dict = {}
        inters_chains1, inters_chains2 = {}, {}
        # seed_entity, prop_name="", entity_type="node"
        used_entities = {}
        entities = {}
        for step in range(depth):
            for ne, entities_list in enumerate(seed_entities):
                for seed_entity, prop_name, entity_type in entities_list:
                    ent_inters_chains1, ent_inters_chains2 = [], []
                    another_entities_list = [entities_list2 for entities_list2 in seed_entities
                                            if entities_list2 != entities_list]
                    another_entities1, another_entities2 = [], {}
                    for entities_list2 in another_entities_list:
                        for ent, *_ in entities_list2:
                            another_entities1.append(ent.lower())
                    if insert_underscores:
                        seed_entity = seed_entity.replace(" ", "_")
                    seed_entity = seed_entity.lower()
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
                                cur_triplets_info, cur_inters_chains1, cur_inters_chains2 = self.parse_triplet_output(
                                    "forw", [entity, None, "object"], another_entities1, another_entities2, chain
                                )
                                ent_inters_chains1, ent_inters_chains2 = \
                                    self.add_chains(ent_inters_chains1, ent_inters_chains2, cur_inters_chains1, cur_inters_chains2)
                                for triplet in cur_triplets_info:
                                    triplets_info.append([(step, "forw", seed_entity, triplet[0][1]["type"])] + triplet)
                                cur_triplets_info, cur_inters_chains1, cur_inters_chains2 = self.parse_triplet_output(
                                    "backw", [None, entity, "object"], another_entities1, another_entities2, chain
                                )
                                ent_inters_chains1, ent_inters_chains2 = \
                                    self.add_chains(ent_inters_chains1, ent_inters_chains2, cur_inters_chains1, cur_inters_chains2)
                                for triplet in cur_triplets_info:
                                    triplets_info.append([(step, "backw", seed_entity, triplet[0][1]["type"])] + triplet)
                                used_entities[(seed_entity, ne)].add((entity, prop_name, tp))
                            elif tp == "rel_prop" and use_rel_props:
                                query = self.extract_triplets_rel_prop_template.format(
                                    prop_name=prop_name,
                                    prop_value=entity.capitalize()
                                )
                                cur_triplets_info, cur_inters_chains1, cur_inters_chains2 = self.parse_triplet_output(
                                    "forw/backw", query, another_entities1, another_entities2, chain, subj_labels, obj_labels
                                )
                                ent_inters_chains1, ent_inters_chains2 = \
                                    self.add_chains(ent_inters_chains1, ent_inters_chains2, cur_inters_chains1, cur_inters_chains2)
                                for triplet in cur_triplets_info:
                                    triplets_info.append([(step, "forw", seed_entity, triplet[0][1]["type"])] + triplet)
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

                    if seed_entity not in inters_chains1:
                        inters_chains1[seed_entity] = ent_inters_chains1
                    else:
                        inters_chains1[seed_entity] += ent_inters_chains1
                    if seed_entity not in inters_chains2:
                        inters_chains2[seed_entity] = ent_inters_chains2
                    else:
                        inters_chains2[seed_entity] += ent_inters_chains2
        return triplets_dict, inters_chains1, inters_chains2