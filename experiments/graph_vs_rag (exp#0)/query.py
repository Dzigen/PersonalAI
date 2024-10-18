from neo4j_functions import Neo4jConnection

conn = Neo4jConnection(uri="bolt://31.207.47.254:7687", user="neo4j", pwd="password")

# Geoffrey has positive, negative or neutral opinion about 1080 processor of X70Pro?
# Jaden has positive, negative or neutral opinion about battery life of K20Pro?

query = """MATCH (a)-[r]-(b) WHERE a.name="K20Pro" AND b.name="battery_life" AND r.person="Jaden"
RETURN a.name as device, r.person as person, type(r) as opinion, b.name as feature"""

res = conn.execute_query(query, db="testdb")
print(res)