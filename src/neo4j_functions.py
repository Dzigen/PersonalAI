import copy
from neo4j import GraphDatabase

class Neo4jConnection:
    def __init__(self, uri, user, pwd, default_db="testdb"):
        self.driver = None
        try:
            self.driver = GraphDatabase.driver(uri, auth=(user, pwd))
        except Exception as e:
            print("Failed to create the driver:", e)
        self.default_db = default_db
        self.execute_query(f"CREATE DATABASE {default_db} IF NOT EXISTS", db=default_db)

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
    
    def extract_triplets_by_query(self, query, max_triplets, db=None):
        # execute query and return triplets in given format or
        # None if query is incorrect or returned triplets list is emtpy
        triplets = []
        try:
            def process_node(node):
                node_props = dict(node)
                name = node_props.get("name", "")
                node_props = {key.replace("_", " "): value.replace("_", " ")
                              for key, value in node_props.items() if key != "name"}
                labels = list(node.labels)
                node_type = ""
                if labels:
                    node_type = labels[0]
                return {"name": name.replace("_", " "), "type": node_type, "prop": node_props}

            def process_rel(rel):
                rel_type = rel.type
                rel_props = dict(rel)
                return {"type": rel_type, "prop": rel_props}

            res = self.execute_query(query, db=db)
            for subj, rel, obj in res:
                triplet = [process_node(subj), process_rel(rel), process_node(obj)]
                triplets.append(triplet)
        except Exception as e:
            print(f"error in extracting triplets: {e}")
        if triplets:
            return triplets
    
    def create_triplets(self, triplets: List[List[Dict]], db=None) -> List[Tuple[str, str, str]]:
        # add nodes and edges which presented in triplets list
        # Check to unique node name
        # Pay attention to the format of triplets

        def create_node_query(node):
            name = node["name"].replace(" ", "_")
            node_type = node["type"].replace(" ", "_")
            props = node["prop"]
            props_query = [f'name: "{name}"']
            for prop_name, prop_value in props.items():
                prop_name_f = prop_name.replace(" ", "_")
                prop_value_f = prop_value.replace(" ", "_")
                props_query.append(f'{prop_name_f}: "{prop_value_f}"')
            props_query = ", ".join(props_query)

            insert_query = f"CREATE (n:{node_type} " + "{" + props_query + "}) RETURN elementId(n) as id"
            return insert_query


        def create_rel(subj, subj_id, rel, obj, obj_id):
            subj_type, rel_type, obj_type = subj["type"].replace(" ", "_"), rel["type"].replace(" ", "_"), obj["type"].replace(" ", "_")
            rel_props = []
            for prop_name, prop_value in rel.get("prop", {}).items():
                rel_props.append(f'{prop_name.replace(" ", "_")}: "{prop_value.replace(" ", "_")}"')
            rel_props = ", ".join(rel_props)

            query = ""
            query += f'MATCH (subj:{subj_type}), (obj:{obj_type}) WHERE elementId(subj) = "{subj_id}" AND elementId(obj) = "{obj_id}" '
            query += f'CREATE (subj)-[rel:{rel_type}' + '{' + rel_props + '}' + ']->(obj) '
            query += 'RETURN elementId(rel) as id'
            return query
        
        added_triplets_ids = []
        for subj, rel, obj in triplets:
            subj_out = self.execute_query(f'MATCH (subj:{subj["type"]}) WHERE subj.name = "{subj["name"]}" RETURN elementID(subj) as id', db=db)
            if not subj_out:
                insert_subj_query = create_node_query(subj)
                subj_id = self.execute_query(insert_subj_query, db=db)[0]['id']
            else:
                subj_id = subj_out[0]['id']

            obj_out = self.execute_query(f'MATCH (obj:{obj["type"]}) WHERE obj.name = "{obj["name"]}" RETURN elementID(obj) as id', db=db)
            if not obj_out:
                insert_obj_query = create_node_query(obj)
                obj_id = self.execute_query(insert_obj_query, db=db)[0]['id']
            else:
                obj_id = obj_out[0]['id']
            
            create_rel_query = create_rel(subj, subj_id, rel, obj, obj_id)
            rel_id = self.execute_query(create_rel_query, db=db)[0]['id']
            added_triplets_ids.append((subj_id, rel_id, obj_id))
        
        return added_triplets_ids

    def delete_triplets(self, triplets, db=None):
        # delete edges which presented in triplets list
        # Pay attention to the format of triplets and check if triplets indeed are in graph
        # If some node loss its last edge, it must be deleted too
        # This method return list of deleted nodes in format which appears in triplets 
        # (only if this nodes haven't type "thesis" or "episodic")
        for subj, rel, obj in triplets:
            try:
                subj_type = subj["type"].replace(" ", "_")
                subj_name = subj["name"].replace(" ", "_")
                obj_type = obj["type"].replace(" ", "_")
                obj_name = obj["name"].replace(" ", "_")
                rel_type = rel["type"].replace(" ", "_")
                rel_props = rel["prop"]
                query = "MATCH "
                query += f'(n:{subj_type}' + ' { ' + f'name: "{subj_name}"' + ' })-'
                props_query = []
                for prop_name, prop_value in rel_props.items():
                    prop_name_f = prop_name.replace(" ", "_")
                    prop_value_f = prop_value.replace(" ", "_")
                    props_query.append(f'{prop_name_f}: "{prop_value_f}"')
                props_query = ", ".join(props_query)
                query += f'[r:{rel_type} ' + '{ ' + props_query + ' }]'
                query += f'->(n:{obj_type}' + ' { ' + f'name: "{obj_name}"' + ' })'
                self.execute_query(query, db=db)
            except Exception as e:
                print(f"error in deleting triplets: {e}")
        return []

    def execute_query(self, query, db=None):
        if db is None:
            db = self.default_db
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
        if db is None:
            db = self.default_db
        query = self.create_node_template.format(type=node_type, name=node_name)
        self.execute_query(query, db=db)

    def create_relationship_no_props(self, type1, type2, name1, name2, rel_name, db=None):
        if db is None:
            db = self.default_db
        query = self.create_rel_template0.format(
            type1=type1,
            type2=type2,
            name1=name1,
            name2=name2,
            rel_name=rel_name
        )
        self.execute_query(query, db=db)

    def create_relationship(self, type1, type2, name1, name2, rel_name, rel_prop_name, rel_prop_value, db=None):
        if db is None:
            db = self.default_db
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
        if db is None:
            db = self.default_db
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
        if db is None:
            db = self.default_db
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
        if db is None:
            db = self.default_db
        if node_type and node_name:
            query = self.extract_node_type_name_template.format(type=node_type, name=node_name)
        elif node_type:
            query = self.extract_node_type_template.format(type=node_type)
        elif node_name:
            query = self.extract_node_name_template.format(name=node_name)
        res = self.execute_query(query, db=db)
        return res

    def extract_triplets(self, name1=None, name2=None, rel=None, db=None):
        if db is None:
            db = self.default_db
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

    def parse_triplet_output(self, query, another_entities, chain, subj_labels=None, obj_labels=None, db=None):
        if db is None:
            db = self.default_db
        triplets = []
        inters_chains = []
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
                                {list(element["b"].labels)[0]: element["b"]["name"]}]
                    triplets.append(triplet)
                    new_chain = copy.deepcopy(chain)
                    if triplet not in new_chain \
                            and (list(triplet[0].values())[0].replace("_", " ") in another_entities \
                                    or list(triplet[-1].values())[0].replace("_", " ") in another_entities) \
                                    or any([prop_value in another_entities for prop_value in triplet[2].values()]):
                        new_chain.append(triplet)
                        inters_chains.append(new_chain)
                    else:
                        new_chain.append(triplet)
                    if (element["a"]["name"], "", "node", new_chain) not in new_entities:
                        new_entities.append((element["a"]["name"], "", "node", new_chain))
                    if (element["b"]["name"], "", "node", new_chain) not in new_entities:
                        new_entities.append((element["b"]["name"], "", "node", new_chain))
        except Exception as e:
            print(f"error in query execution: {e}")
        return triplets, new_entities, inters_chains

    def bfs(self, seed_entities, depth=1, subj_labels=None, obj_labels=None, db=None):
        if db is None:
            db = self.default_db
        triplets_dict = {}
        inters_chains = []
        # seed_entity, prop_name="", entity_type="node"
        for entities_list in seed_entities:
            for seed_entity, prop_name, entity_type in entities_list:
                another_entities_list = [entities_list2 for entities_list2 in seed_entities
                                         if entities_list2 != entities_list]
                another_entities = []
                for entities_list2 in another_entities_list:
                    for ent, *_ in entities_list2:
                        another_entities.append(ent)
                seed_entity = seed_entity.replace(" ", "_")
                used_entities = set()
                entities = [(seed_entity, prop_name, entity_type, [])]
                for step in range(depth):
                    new_entities = []
                    for entity, prop_name, tp, chain in entities:
                        if (entity, prop_name, tp) not in used_entities:
                            if tp == "node":
                                query = self.extract_triplets_name1_template.format(name1=entity)
                                new_triplets, cur_entities, cur_inters_chains = self.parse_triplet_output(
                                    query, another_entities, chain, subj_labels, obj_labels, db
                                )
                                for ch in cur_inters_chains:
                                    if ch not in inters_chains:
                                        inters_chains.append(ch)
                                for triplet in new_triplets:
                                    if (step, "forw", triplet[1]) not in triplets_dict:
                                        triplets_dict[(step, "forw", triplet[1])] = []
                                    if triplet not in triplets_dict[(step, "forw", triplet[1])]:
                                        triplets_dict[(step, "forw", triplet[1])].append(triplet)
                                for ent in cur_entities:
                                    if ent not in new_entities:
                                        new_entities.append(ent)
                                query = self.extract_triplets_name2_template.format(name2=entity)
                                new_triplets, cur_entities, cur_inters_chains = self.parse_triplet_output(
                                    query, another_entities, chain, subj_labels, obj_labels, db
                                )
                                for ch in cur_inters_chains:
                                    if ch not in inters_chains:
                                        inters_chains.append(ch)
                                for triplet in new_triplets:
                                    if (step, "backw", triplet[1]) not in triplets_dict:
                                        triplets_dict[(step, "backw", triplet[1])] = []
                                    if triplet not in triplets_dict[(step, "backw", triplet[1])]:
                                        triplets_dict[(step, "backw", triplet[1])].append(triplet)
                                for ent in cur_entities:
                                    if ent not in new_entities:
                                        new_entities.append(ent)
                                used_entities.add((entity, prop_name, tp))
                            elif tp == "rel_prop":
                                query = self.extract_triplets_rel_prop_template.format(prop_name=prop_name, prop_value=entity)
                                new_triplets, cur_entities, cur_inters_chains = self.parse_triplet_output(
                                    query, another_entities, chain, subj_labels, obj_labels, db
                                )
                                for ch in cur_inters_chains:
                                    if ch not in inters_chains:
                                        inters_chains.append(ch)
                                for triplet in new_triplets:
                                    if (step, "forw", triplet[1]) not in triplets_dict:
                                        triplets_dict[(step, "forw", triplet[1])] = []
                                    if triplet not in triplets_dict[(step, "forw", triplet[1])]:
                                        triplets_dict[(step, "forw", triplet[1])].append(triplet)
                                for ent in cur_entities:
                                    if ent not in new_entities:
                                        new_entities.append(ent)
                                used_entities.add((entity, prop_name, tp))
                    entities += new_entities
        return triplets_dict, inters_chains


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