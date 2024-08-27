import copy
from neo4j import GraphDatabase

class Neo4jConnection:
    def __init__(self, uri, user, pwd):
        self.driver = None
        try:
            self.driver = GraphDatabase.driver(uri, auth=(user, pwd))
        except Exception as e:
            print("Failed to create the driver:", e)
        self.create_node_template = 'CREATE (n:{type} {{ name: "{name}"}})'
        self.create_rel_template0 = """MATCH (a:{type1}), (b:{type2})
WHERE a.name="{name1}" and b.name ="{name2}"
CREATE (a)-[r:{rel_name}]->(b)"""
        self.create_rel_template1 = """MATCH (a:{type1}), (b:{type2})
WHERE a.name="{name1}" and b.name ="{name2}"
CREATE (a)-[r:{rel_name} {{{rel_prop_name}: "{rel_prop_value}"}}]->(b)"""
        self.create_rel_template2 = """MATCH (a:{type1}), (b:{type2})
WHERE a.name="{name1}" and b.name ="{name2}"
CREATE (a)-[r:{rel_name} {{{rel_prop_name1}: "{rel_prop_value1}", {rel_prop_name2}: "{rel_prop_value2}"}}]->(b)"""
        self.create_rel_template5 = """MATCH (a:{type1}), (b:{type2})
WHERE a.name="{name1}" and b.name ="{name2}"
CREATE (a)-[r:{rel_name} {{{rel_prop_name1}: "{rel_prop_value1}", {rel_prop_name2}: "{rel_prop_value2}", {rel_prop_name3}: "{rel_prop_value3}", {rel_prop_name4}: "{rel_prop_value4}", {rel_prop_name5}: "{rel_prop_value5}"}}]->(b)"""

        self.extract_node_type_template = 'MATCH (a:{type}) RETURN a'
        self.extract_node_name_template = 'MATCH (a) WHERE a.name="{name}" RETURN a'
        self.extract_node_type_name_template = 'MATCH (a:{type}) WHERE a.name="{name}" RETURN a'

        # MATCH (a:User {username: 'user6'})-[r]-(b) RETURN r, a, b
        self.extract_triplets_name1_template = 'MATCH (a)-[r]-(b) WHERE a.name="{name1}" RETURN a, r, b'
        self.extract_triplets_name2_template = 'MATCH (a)-[r]-(b) WHERE b.name="{name2}" RETURN a, r, b'
        self.extract_triplets_names_template = 'MATCH (a)-[r]-(b) WHERE a.name="{name1}" AND b.name="{name2}" RETURN a, r, b'
        self.extract_triplets_name1_rel_template = 'MATCH (a)-[r:{rel}]-(b) WHERE a.name="{name1}" RETURN a, r, b'
        self.extract_triplets_name2_rel_template = 'MATCH (a)-[r:{rel}]-(b) WHERE b.name="{name2}" RETURN a, r, b'
        self.extract_triplets_rel_template = 'MATCH (a)-[r:{rel}]-(b) RETURN a, r, b'
        self.extract_triplets_rel_prop_template = 'MATCH (a)-[r]-(b) WHERE r.{prop_name}="{prop_value}" RETURN a, r, b'

    def close(self):
        if self.driver is not None:
            self.driver.close()

    def execute_query(self, query, db=None):
        assert self.driver is not None, "Driver not initialized!"
        session = None
        response = None
        try:
            session = self.driver.session(database=db) if db is not None else self.driver.session()
            response = list(session.run(query))
        except Exception as e:
            print("Query failed:", e)
        finally:
            if session is not None:
                session.close()
        return response

    def create_node(self, node_type, node_name, db=None):
        query = self.create_node_template.format(type=node_type, name=node_name)
        self.execute_query(query, db=db)

    def create_relationship_no_props(self, type1, type2, name1, name2, rel_name, db=None):
        query = self.create_rel_template0.format(
            type1=type1,
            type2=type2,
            name1=name1,
            name2=name2,
            rel_name=rel_name
        )
        self.execute_query(query, db=db)

    def create_relationship(self, type1, type2, name1, name2, rel_name, rel_prop_name, rel_prop_value, db=None):
        query = self.create_rel_template1.format(
            type1=type1,
            type2=type2,
            name1=name1,
            name2=name2,
            rel_name=rel_name,
            rel_prop_name=rel_prop_name,
            rel_prop_value=rel_prop_value
        )
        self.execute_query(query, db=db)

    def create_relationship_2props(self, type1, type2, name1, name2, rel_name, rel_prop_name1, rel_prop_value1,
                                         rel_prop_name2, rel_prop_value2, db=None):
        query = self.create_rel_template2.format(
            type1=type1,
            type2=type2,
            name1=name1,
            name2=name2,
            rel_name=rel_name,
            rel_prop_name1=rel_prop_name1,
            rel_prop_value1=rel_prop_value1,
            rel_prop_name2=rel_prop_name2,
            rel_prop_value2=rel_prop_value2
        )
        self.execute_query(query, db=db)

    def create_relationship_5props(self, type1, type2, name1, name2, rel_name,
                                   rel_prop_name1, rel_prop_value1,
                                   rel_prop_name2, rel_prop_value2,
                                   rel_prop_name3, rel_prop_value3,
                                   rel_prop_name4, rel_prop_value4,
                                   rel_prop_name5, rel_prop_value5, db=None):
        query = self.create_rel_template5.format(
            type1=type1,
            type2=type2,
            name1=name1,
            name2=name2,
            rel_name=rel_name,
            rel_prop_name1=rel_prop_name1,
            rel_prop_value1=rel_prop_value1,
            rel_prop_name2=rel_prop_name2,
            rel_prop_value2=rel_prop_value2,
            rel_prop_name3=rel_prop_name3,
            rel_prop_value3=rel_prop_value3,
            rel_prop_name4=rel_prop_name4,
            rel_prop_value4=rel_prop_value4,
            rel_prop_name5=rel_prop_name5,
            rel_prop_value5=rel_prop_value5
        )
        self.execute_query(query, db=db)

    def extract_node(self, node_type=None, node_name=None, db=None):
        if node_type and node_name:
            query = self.extract_node_type_name_template.format(type=node_type, name=node_name)
        elif node_type:
            query = self.extract_node_type_template.format(type=node_type)
        elif node_name:
            query = self.extract_node_name_template.format(name=node_name)
        res = self.execute_query(query, db=db)
        return res

    def extract_triplets(self, name1=None, name2=None, rel=None, db=None):
        if name1 and name2:
            query = self.extract_triplets_names_template.format(name1=name1, name2=name2)
        elif name1 and rel:
            query = self.extract_triplets_name1_rel_template.format(rel=rel, name1=name1)
        elif name2 and rel:
            query = self.extract_triplets_name2_rel_template.format(rel=rel, name2=name2)
        elif name1:
            query = self.extract_triplets_name1_template.format(name1=name1)
        elif name2:
            query = self.extract_triplets_name2_template.format(name2=name2)
        elif rel:
            query = self.extract_triplets_rel_template.format(rel=rel)
        res = self.execute_query(query, db=db)
        return res

    def parse_triplet_output(self, direction, query, another_entities1, another_entities2, chain, subj_labels=None,
                             obj_labels=None, db=None):
        triplets = []
        inters_chains1, inters_chains2 = [], []
        new_entities = []
        try:
            res = self.execute_query(query, db=db)
            for element in res:
                rel_props = dict(element["r"])
                rel_props = {key: value for key, value in rel_props.items() if key not in ["raw_time", "sentiment"]}
                if (subj_labels is None or set(element["a"].labels).intersection(set(subj_labels))) \
                        and (obj_labels is None or set(element["b"].labels).intersection(set(obj_labels))):
                    triplet = [{list(element["a"].labels)[0]: element["a"]["name"]},
                               element["r"].type,
                               rel_props,
                               {list(element["b"].labels)[0]: element["b"]["name"]},
                               direction]
                    triplets.append(triplet)
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
                        subj = list(triplet[0].values())[0].replace("_", " ")
                        obj = list(triplet[-2].values())[0].replace("_", " ")
                        if (subj in another_entities1 or obj in another_entities1) \
                                or any([prop_value in another_entities1 for prop_value in triplet[2].values()]):
                            new_chain.append(triplet)
                            inters_chains1.append(new_chain)
                        elif "backw" in direction and subj in another_entities2:
                            new_chain.append(triplet)
                            second_chain = another_entities2[subj]
                            persons = count_persons(new_chain, second_chain)
                            if not ([ch[-1] for ch in new_chain] == ["forw", "backw"] \
                                    and [ch[-1] for ch in second_chain] == ["forw", "backw"]) and len(persons) < 3:
                                inters_chains2.append([new_chain, second_chain, ["backw", subj]])
                        elif "forw" in direction and obj in another_entities2:
                            new_chain.append(triplet)
                            second_chain = another_entities2[obj]
                            persons = count_persons(new_chain, second_chain)
                            if not ([ch[-1] for ch in new_chain] == ["forw", "backw"] \
                                    and [ch[-1] for ch in second_chain] == ["forw", "backw"]) and len(persons) < 3:
                                inters_chains2.append([new_chain, second_chain, ["forw", obj]])
                        elif any([prop_value in another_entities2 for prop_value in triplet[2].values()]):
                            for prop_value in triplet[2].values():
                                if prop_value in another_entities2:
                                    new_chain.append(triplet)
                                    second_chain = another_entities2[prop_value]
                                    persons = count_persons(new_chain, second_chain)
                                    if len(persons) < 3:
                                        inters_chains2.append([new_chain, second_chain, ["prop", prop_value]])
                        else:
                            new_chain.append(triplet)
                    else:
                        new_chain.append(triplet)
                    if (element["a"]["name"], "", "node", new_chain) not in new_entities:
                        new_entities.append((element["a"]["name"], "", "node", new_chain))
                    if (element["b"]["name"], "", "node", new_chain) not in new_entities:
                        new_entities.append((element["b"]["name"], "", "node", new_chain))
        except Exception as e:
            print(f"error in query execution: {e}")
        return triplets, new_entities, inters_chains1, inters_chains2

    def add_chains(self, inters_chains1, inters_chains2, cur_inters_chains1, cur_inters_chains2):
        for ch in cur_inters_chains1:
            if ch not in inters_chains1:
                inters_chains1.append(ch)
        for ch in cur_inters_chains2:
            if ch not in inters_chains2:
                inters_chains2.append(ch)
        return inters_chains1, inters_chains2

    def bfs(self, seed_entities, depth=1, subj_labels=None, obj_labels=None, db=None):
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
                            another_entities1.append(ent)
                    seed_entity = seed_entity.replace(" ", "_")
                    if step == 0:
                        used_entities[(seed_entity, ne)] = set()
                        entities[(seed_entity, ne)] = [(seed_entity, prop_name, entity_type, [])]
                    for (cur_seed_entity, cur_ne), entities_info in entities.items():
                        if cur_ne != ne:
                            for entity, *_, chain in entities_info:
                                if entity.lower() != cur_seed_entity.lower() and entity.lower() != seed_entity.lower() \
                                        and entity not in another_entities1 and entity not in another_entities2:
                                    another_entities2[entity] = chain

                    new_entities = []
                    for entity, prop_name, tp, chain in entities[(seed_entity, ne)]:
                        if (entity, prop_name, tp) not in used_entities[(seed_entity, ne)]:
                            if tp == "node":
                                query = self.extract_triplets_name1_template.format(name1=entity)
                                new_triplets, cur_entities, cur_inters_chains1, cur_inters_chains2 = self.parse_triplet_output(
                                    "forw", query, another_entities1, another_entities2, chain, subj_labels, obj_labels, db
                                )
                                inters_chains1, inters_chains2 = \
                                    self.add_chains(inters_chains1, inters_chains2, cur_inters_chains1, cur_inters_chains2)
                                for triplet in new_triplets:
                                    if (step, "forw", triplet[1]) not in triplets_dict:
                                        triplets_dict[(step, "forw", seed_entity, triplet[1])] = []
                                    if triplet not in triplets_dict[(step, "forw", seed_entity, triplet[1])]:
                                        triplets_dict[(step, "forw", seed_entity, triplet[1])].append(triplet)
                                for ent in cur_entities:
                                    if ent not in new_entities:
                                        new_entities.append(ent)
                                query = self.extract_triplets_name2_template.format(name2=entity)
                                new_triplets, cur_entities, cur_inters_chains1, cur_inters_chains2 = self.parse_triplet_output(
                                    "backw", query, another_entities1, another_entities2, chain, subj_labels, obj_labels, db
                                )
                                inters_chains1, inters_chains2 = \
                                    self.add_chains(inters_chains1, inters_chains2, cur_inters_chains1, cur_inters_chains2)
                                for triplet in new_triplets:
                                    if (step, "backw", triplet[1]) not in triplets_dict:
                                        triplets_dict[(step, "backw", seed_entity, triplet[1])] = []
                                    if triplet not in triplets_dict[(step, "backw", seed_entity, triplet[1])]:
                                        triplets_dict[(step, "backw", seed_entity, triplet[1])].append(triplet)
                                for ent in cur_entities:
                                    if ent not in new_entities:
                                        new_entities.append(ent)
                                used_entities[(seed_entity, ne)].add((entity, prop_name, tp))
                            elif tp == "rel_prop":
                                query = self.extract_triplets_rel_prop_template.format(prop_name=prop_name, prop_value=entity)
                                new_triplets, cur_entities, cur_inters_chains1, cur_inters_chains2 = self.parse_triplet_output(
                                    "forw/backw", query, another_entities1, another_entities2, chain, subj_labels, obj_labels, db
                                )
                                inters_chains1, inters_chains2 = \
                                    self.add_chains(inters_chains1, inters_chains2, cur_inters_chains1, cur_inters_chains2)
                                for triplet in new_triplets:
                                    if (step, "forw", seed_entity, triplet[1]) not in triplets_dict:
                                        triplets_dict[(step, "forw", seed_entity, triplet[1])] = []
                                    if triplet not in triplets_dict[(step, "forw", seed_entity, triplet[1])]:
                                        triplets_dict[(step, "forw", seed_entity, triplet[1])].append(triplet)
                                for ent in cur_entities:
                                    if ent not in new_entities:
                                        new_entities.append(ent)
                                used_entities[(seed_entity, ne)].add((entity, prop_name, tp))
                    entities[(seed_entity, ne)] += new_entities
        return triplets_dict, inters_chains1, inters_chains2


if __name__ == "__main__":
    conn = Neo4jConnection(uri="bolt://31.207.47.254:7687", user="neo4j", pwd="password")

    # создание базы данных

    conn.execute_query("CREATE DATABASE testdb IF NOT EXISTS")

    # Создание узлов графа

    conn.create_node(node_type="smartphone", node_name="Xiaomi 11", db="testdb")
    conn.create_node(node_type="feature", node_name="WiFi module", db="testdb")

    # Создание relation между узлами (rel_prop_name - название property для связи между узлами)

    conn.create_relationship(
        type1="smartphone",
        type2="feature",
        name1="Xiaomi 11",
        name2="WiFi module",
        rel_name="opinion",
        rel_prop_name="dialog_id",
        rel_prop_value="12345",
        db="testdb"
    )

    # Извлечение узлов

    res = conn.extract_node(node_name="Xiaomi 11", db="testdb")
    print(res)

    # extract all smartphones
    res = conn.extract_node(node_type="smartphone", db="testdb")
    print(res)

    res = conn.extract_node(node_type="smartphone", node_name="Xiaomi 11", db="testdb")
    print(res)

    # извлечение триплетов
    res = conn.extract_triplets(name1="Xiaomi 11", db="testdb")
    print(res)

    res = conn.extract_triplets(name2="WiFi module", db="testdb")
    print(res)

    res = conn.extract_triplets(rel="opinion", db="testdb")
    print(res)

    res = conn.extract_triplets(name1="Xiaomi 11", rel="opinion", db="testdb")
    print(res)

# MATCH (n) RETURN (n) - извлечь все узлы