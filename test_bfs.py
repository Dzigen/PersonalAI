from neo4j_functions import Neo4jConnection

conn = Neo4jConnection(uri="bolt://31.207.47.254:7687", user="neo4j", pwd="password")

#triplets_dict = conn.bfs("Maria", prop_name="person", entity_type="rel_prop", depth=2, subj_labels=["device"], db="testdb")
#triplets_dict, inters_chains = conn.bfs([("Xiaomi_11", "", "node"), ("battery life", "", "node")], db="testdb")
triplets_dict, inters_chains = conn.bfs([[("Xiaomi_11", "", "node")], [("Rodrigo", "", "node")]], db="testdb")
#triplets_dict, inters_chains = conn.bfs([("Jane", "", "node"), ("Jonathan", "", "node")], depth=2, db="testdb")

for chain in inters_chains:
    print("----- chain:", chain)

for (step, direction, rel), triplets in triplets_dict.items():
    triplets_formatted = []
    for subj, rel, rel_props, obj in triplets[:6]:
        subj = {key.replace("_", " "): value.replace("_", " ") for key, value in subj.items()}
        obj = {key.replace("_", " "): value.replace("_", " ") for key, value in obj.items()}
        rel_props = {key.replace("_", " "): value.replace("_", " ") for key, value in rel_props.items()}
        subj_str = ", ".join([f"{key}: {value}" for key, value in subj.items()])
        obj_str = ", ".join([f"{key}: {value}" for key, value in obj.items()])
        if rel_props:
            rel_props_str = ", ".join([f"{key}: {value}" for key, value in rel_props.items()])
            triplets_formatted.append(f"{rel_props_str}, {subj_str}, {obj_str}")
        else:
            triplets_formatted.append(f"{subj_str} {rel} {obj_str}")
    with open("bfs_res.txt", 'a') as out:
        for triplet in triplets_formatted:
            out.write(f"{step} --- {direction} --- {rel} --- {triplet}"+'\n')