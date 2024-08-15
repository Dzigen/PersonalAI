from neo4j_functions import Neo4jConnection

conn = Neo4jConnection(uri="bolt://31.207.47.254:7687", user="neo4j", pwd="password")

triplets = conn.bfs("Maria", prop_name="person", entity_type="rel_prop", depth=1, subj_labels=["device"], db="testdb")