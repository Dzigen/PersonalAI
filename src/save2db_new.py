import copy
import json
from collections import Counter
from neo4j_functions import Neo4jConnection

with open("Augment_DiaASQ.json", 'r') as inp:
    data = json.load(inp)

print(len(data["data"]))
samples = [element for element in data["data"] if "_" not in element.get("doc_id", "")]
print(len(samples))

conn = Neo4jConnection(uri="bolt://31.207.47.254:7687", user="neo4j", pwd="password")

all_devices = set()
insert = False
total_triplets = []
good_samples = []
good_dialogs = 0
person_triplets = set()
entities = set()
for n, sample in list(enumerate(samples)):
    triplets = sample["clean_triplets"]
    sentences = sample["sentences"]
    speakers = sample["speakers"]
    time = sample["time"].split(",")[0]
    raw_time = sample["raw_time"]
    if "speakers_names" in sample:
        speakers_names = sample["speakers_names"]
    else:
        speakers_names = sample["speakers"]
    cur_questions = sample.get("questions", "")
    new_questions = []
    for q_element in cur_questions:
        q_text = q_element["question"]
        q_text = f"{q_text.replace('?', '')} on {time}?"
        q_element["question"] = q_text
        new_questions.append(q_element)
    sample["questions"] = new_questions

    f_triplets = []
    for triplet in triplets:
        subj, obj, rel_data = triplet
        person = rel_data["speaker"]
        rel = rel_data["label"]
        if len(rel) > 1 and not rel[0].isdigit() and person and len(person.split()) == 1 \
                and person.lower() != "unidentified" and person in speakers_names:
            f_triplets.append(triplet)
    if f_triplets:
        good_dialogs += 1
        new_sample = {
            key: value for key, value in sample.items()
            if key in ["doc_id", "sentences", "speakers", "questions", "speakers_names"]
        }

        sentences = sample["sentences"]
        sentences = [f"{speaker}: {sentence}" for speaker, sentence in zip(speakers_names, sentences)]
        new_sample["sentences"] = sentences
        new_sample["speakers"] = ", ".join([str(element) for element in new_sample["speakers"]])

        new_sample["clean_triplets"] = f_triplets
        new_sample["questions"] = [question for question in new_sample["questions"]
                                   if not question["question"].startswith("The majority")]
        good_samples.append(new_sample)

        for subj, obj, rel_data in f_triplets:
            rel = rel_data["label"]
            speaker = rel_data["speaker"]
            sentiment = rel_data["sentiment"]
            subj = subj.replace(" ", "_")
            rel = rel.strip('"')
            for symb in "'.-,!?":
                rel = rel.replace(symb, "")
            rel = rel.replace('"', '').replace(" ", "_")
            obj = obj.replace(" ", "_")
            if len(subj) > 1 and len(rel) > 1 and len(rel.split("_")) < 5:
                total_triplets.append([subj, obj, rel_data])
                entities.add((subj, "device"))
                entities.add((obj, "feature"))
                if insert:
                    person_triplets.add((subj, "has_device", speaker))
                    print(n, subj, rel, obj, sentiment, speaker)
                    res1 = conn.extract_node(node_type="device", node_name=subj, db="testdb")
                    if not res1:
                        conn.create_node(node_type="device", node_name=subj, db="testdb")
                    res2 = conn.extract_node(node_type="feature", node_name=obj, db="testdb")
                    if not res2:
                        conn.create_node(node_type="feature", node_name=obj, db="testdb")
                    all_devices.add(subj)
                    conn.create_relationship_5props(
                        type1="device",
                        type2="feature",
                        name1=subj,
                        name2=obj,
                        rel_name="opinion",
                        rel_prop_name1="opinion",
                        rel_prop_value1=rel,
                        rel_prop_name2="person",
                        rel_prop_value2=speaker,
                        rel_prop_name3="sentiment",
                        rel_prop_value3=sentiment,
                        rel_prop_name4="time",
                        rel_prop_value4=time,
                        rel_prop_name5="raw_time",
                        rel_prop_value5=raw_time,
                        db="testdb"
                    )

for subj, rel, person in person_triplets:
    print(subj, rel, person)
    entities.add((person, "person"))
    if insert:
        res1 = conn.extract_node(node_type="person", node_name=person, db="testdb")
        if not res1:
            conn.create_node(node_type="person", node_name=person, db="testdb")
        conn.create_relationship_no_props(
            type1="person",
            type2="device",
            name1=person,
            name2=subj,
            rel_name=rel,
            db="testdb"
        )

manf_dict = {"Xiaomi": "Xiaomi", "Apple": "Apple", "OnePlus": "OnePlus", "Vivo": "Vivo", "Honor": "Honor",
             "Huawei": "Huawei", "Samsung": "Samsung", "Redmi": "Xiaomi", "Iphone": "Apple", "One Plus": "OnePlus"}

for manf in manf_dict.values():
    entities.add((manf, "manufacturer"))

if insert:
    for manf in manf_dict.values():
        conn.create_node(node_type="manufacturer", node_name=manf, db="testdb")

    for device in all_devices:
        found_manf = ""
        for manf in manf_dict:
            if device.lower() == manf.lower():
                found_manf = manf_dict[manf]
            elif any([tok == manf.lower() for tok in device.lower().split()]):
                found_manf = manf_dict[manf]
        if found_manf:
            conn.create_relationship_no_props(
                type1="device",
                type2="manufacturer",
                name1=device,
                name2=found_manf,
                rel_name="manufacturer",
                db="testdb"
            )

mult_rels, mult_subj = 0, 0
stats1, stats2 = {}, {}
for subj, obj, rel_data in total_triplets:
    rel = rel_data["label"]
    sent = rel_data["sentiment"]
    if (subj, obj) not in stats1:
        stats1[(subj, obj)] = []
    stats1[(subj, obj)].append((rel, sent))
    if obj not in stats2:
        stats2[obj] = []
    stats2[obj].append((subj, rel, sent))

stats1 = {subj_obj: rel_sent for subj_obj, rel_sent in stats1.items() if len(rel_sent) > 1}
stats1 = list(stats1.items())
stats1 = sorted(stats1, key=lambda x: len(x[1]), reverse=True)

stats2 = {obj: subj_rel for obj, subj_rel in stats2.items() if len(subj_rel) > 1}
stats2 = list(stats2.items())
stats2 = sorted(stats2, key=lambda x: len(x[1]), reverse=True)

print("multiple rels", len(stats1))
print("multiple subjects", len(stats2))

with open("multiple_rels.json", 'w') as out:
    json.dump(stats1, out, indent=2)

with open("multiple_subjects.json", 'w') as out:
    json.dump(stats2, out, indent=2)

with open("multiple_subjects.txt", 'w') as out:
    for obj, subj_rel in stats2[:15]:
        subj_rel = sorted(subj_rel, key=lambda x: x[0])
        out.write(f"----- {obj}"+'\n')
        for element in subj_rel:
            out.write(str(element)+'\n')
        out.write("\n")

utterances, questions = [], []
with open("good_examples.json", 'w', encoding="utf8") as out:
    json.dump(good_samples[:10], out, indent=2, ensure_ascii=False)

for sample in good_samples:
    utterances += sample["sentences"]
    questions += sample["questions"]

with open("utterances_for_test.json", 'w', encoding="utf8") as out:
    json.dump(utterances, out, indent=2, ensure_ascii=False)

with open("questions/device_sentiment.json", 'w', encoding="utf8") as out:
    json.dump(questions[:200], out, indent=2, ensure_ascii=False)

print("good dialogs", good_dialogs)
print("utterances", len(utterances))
print("questions", len(questions))

entities = [list(entity) for entity in entities]

with open("entities.json", 'w') as out:
    json.dump(entities, out, indent=2)