from neo4j_functions import Neo4jConnection

conn = Neo4jConnection(uri="bolt://31.207.47.254:7687", user="neo4j", pwd="password")

#triplets_dict = conn.bfs("Maria", prop_name="person", entity_type="rel_prop", depth=2, subj_labels=["device"], db="testdb")
#triplets_dict, inters_chains = conn.bfs([("Xiaomi_11", "", "node"), ("battery life", "", "node")], db="testdb")
#triplets_dict, inters_chains = conn.bfs([[("Xiaomi_11", "", "node")], [("Rodrigo", "", "node")]], db="testdb")
triplets_dict, inters_chains1, inters_chains2 = conn.bfs([[("Abraham", "", "node")], [("Violet", "", "node")]], depth=2, db="testdb")

chain_triplets1, chain_triplets2 = [], []
chain_subj_obj1 = set()
for chain in inters_chains1:
    for triplet in chain:
        subj = triplet[0].items()
        subj = sorted(subj, key=lambda x: x[1])
        obj = triplet[-2].items()
        obj = sorted(obj, key=lambda x: x[1])
        subj = str(subj)
        obj = str(obj)
        if (subj, obj) not in chain_subj_obj1 and (obj, subj) not in chain_subj_obj1 and triplet not in chain_triplets1:
            chain_triplets1.append(triplet)

for triplet in chain_triplets1:
    with open("bfs_res.txt", 'a') as out:
        out.write(f"----- chain1: {triplet}"+'\n')

chain_subj_obj2 = set()
for chain1, chain2, *_ in inters_chains2:
    for triplet in chain1:
        subj = triplet[0].items()
        subj = sorted(subj, key=lambda x: x[1])
        obj = triplet[-2].items()
        obj = sorted(obj, key=lambda x: x[1])
        subj = str(subj)
        obj = str(obj)
        if (subj, obj) not in chain_subj_obj2 and (obj, subj) not in chain_subj_obj2 and triplet not in chain_triplets2:
            chain_subj_obj2.add((subj, obj))
            chain_triplets2.append(triplet)
    for triplet in chain2:
        subj = triplet[0].items()
        subj = sorted(subj, key=lambda x: x[1])
        obj = triplet[-2].items()
        obj = sorted(obj, key=lambda x: x[1])
        subj = str(subj)
        obj = str(obj)
        if (subj, obj) not in chain_subj_obj2 and (obj, subj) not in chain_subj_obj2 and triplet not in chain_triplets2:
            chain_subj_obj2.add((subj, obj))
            chain_triplets2.append(triplet)

for triplet in chain_triplets2:
    with open("bfs_res.txt", 'a') as out:
        out.write(f"----- chain2: {triplet}"+'\n')

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