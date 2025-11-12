from neo4j_functions import Neo4jConnection

conn = Neo4jConnection(uri="bolt://31.207.47.254:7687",
                       user="neo4j", pwd="password")

# triplets_dict = conn.bfs("Maria", prop_name="person", entity_type="rel_prop", depth=2, subj_labels=["device"], db="testdb")
# triplets_dict, inters_chains = conn.bfs([("Xiaomi_11", "", "node"), ("battery life", "", "node")], db="testdb")
# triplets_dict, inters_chains = conn.bfs([[("Xiaomi_11", "", "node")], [("Rodrigo", "", "node")]], db="testdb")
# triplets_dict, inters_chains1, inters_chains2 = conn.bfs([[("Abraham", "", "node")], [("Violet", "", "node")]], depth=2, db="testdb")
# triplets_dict, inters_chains1, inters_chains2 = conn.bfs([[("Luccile", "person", "rel_prop")]], depth=1, db="testdb")
triplets_dict, inters_chains1, inters_chains2 = conn.bfs([
    [('Luccile', '', 'node')], [('system', '', 'node')], [('Apple', '', 'node')]
], depth=1, db="testdb")
print("triplets_dict", len(triplets_dict), "inters_chains1",
      len(inters_chains1), "inters_chains2", len(inters_chains2))


def process_chain(chain, chain_subj_obj, chain_triplets, cnt):
    for triplet in chain:
        subj = triplet[0].items()
        subj = sorted(subj, key=lambda x: x[1])
        obj = triplet[-2].items()
        obj = sorted(obj, key=lambda x: x[1])
        rel_props = triplet[2].items()
        rel_props = [(key, value)
                     for key, value in rel_props if key not in ["raw_time", "time"]]
        rel_props = sorted(rel_props, key=lambda x: x[0])
        rel_props = str(rel_props)
        subj = str(subj)
        obj = str(obj)
        if (subj, obj, rel_props) not in chain_subj_obj and (obj, subj, rel_props) not in chain_subj_obj \
                and [cnt, triplet] not in chain_triplets:
            chain_triplets.append([cnt, triplet])
            chain_subj_obj.add((subj, obj, rel_props))
    return chain_subj_obj, chain_triplets


def process_inters_chains(inters_chains1, inters_chains2):
    chain_triplets1, chain_triplets2 = [], []
    chain_subj_obj1, chain_subj_obj2 = set(), set()
    inters_chains1 = sorted(inters_chains1, key=lambda x: x[1], reverse=True)
    for chain, cnt in inters_chains1:
        chain_subj_obj1, chain_triplets1 = process_chain(
            chain, chain_subj_obj1, chain_triplets1, cnt)
    for chain1, chain2, *_ in inters_chains2:
        chain_subj_obj2, chain_triplets2 = process_chain(
            chain1, chain_subj_obj2, chain_triplets2, 0)
        chain_subj_obj2, chain_triplets2 = process_chain(
            chain2, chain_subj_obj2, chain_triplets2, 0)
    return chain_triplets1, chain_triplets2


chain_triplets1, chain_triplets2 = process_inters_chains(
    inters_chains1, inters_chains2)

for cnt, triplet in chain_triplets1:
    with open("bfs_res.txt", 'a') as out:
        out.write(f"{cnt} ----- chain1: {triplet}"+'\n')

for cnt, triplet in chain_triplets2:
    with open("bfs_res.txt", 'a') as out:
        out.write(f"----- chain2: {triplet}"+'\n')

for (step, direction, seed_entity, rel), triplets in triplets_dict.items():
    triplets_formatted = []
    for subj, rel, rel_props, obj, *_ in triplets[:30]:
        subj = {key.replace("_", " "): value.replace("_", " ")
                for key, value in subj.items()}
        obj = {key.replace("_", " "): value.replace("_", " ")
               for key, value in obj.items()}
        rel_props = {key.replace("_", " "): value.replace(
            "_", " ") for key, value in rel_props.items()}
        subj_str = ", ".join(
            [f"{key}: {value}" for key, value in subj.items()])
        obj_str = ", ".join([f"{key}: {value}" for key, value in obj.items()])
        if rel_props:
            rel_props_str = ", ".join(
                [f"{key}: {value}" for key, value in rel_props.items()])
            triplets_formatted.append(
                f"{rel_props_str}, {subj_str}, {obj_str}")
        else:
            triplets_formatted.append(f"{subj_str} {rel} {obj_str}")
    with open("bfs_res.txt", 'a') as out:
        for triplet in triplets_formatted:
            out.write(f"{step} --- {direction} --- {rel} --- {triplet}"+'\n')
