from neo4j import GraphDatabase

class Neo4jConnection:
    def __init__(self, uri, user, pwd):
        self.driver = None
        try:
            self.driver = GraphDatabase.driver(uri, auth=(user, pwd))
        except Exception as e:
            print("Failed to create the driver:", e)
        self.create_node_template = 'CREATE (n:{type} {{ name: "{name}"}})'
        self.create_rel_template1 = """MATCH (a:{type1}), (b:{type2})
WHERE a.name="{name1}" and b.name ="{name2}"
CREATE (a)-[r:{rel_name} {{{rel_prop_name}: "{rel_prop_value}"}}]->(b)"""
        self.create_rel_template2 = """MATCH (a:{type1}), (b:{type2})
WHERE a.name="{name1}" and b.name ="{name2}"
CREATE (a)-[r:{rel_name} {{{rel_prop_name1}: "{rel_prop_value1}", {rel_prop_name2}: "{rel_prop_value2}"}}]->(b)"""

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