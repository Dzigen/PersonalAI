import json
import random

random.seed(1)

with open("Clean_DiaASQ.json", 'r') as inp:
    data = json.load(inp)
samples = [element for element in data["data"] if "_" not in element["doc_id"]]

total_triplets = []
for sample in samples:
    triplets = sample["clean_triplets"]
    speakers = sample["speakers"]
    speakers_names = sample["speakers_names"]
    found = True
    for triplet in triplets:
        subj, obj, rel_data = triplet
        person = rel_data["speaker"]
        if person != "Unidentified" and person not in speakers_names:
            found = False
    if found:
        old_triplets = sample["clean_triplets"]
        tr2sp = {}
        for triplet in old_triplets:
            subj, obj, rel_data = triplet
            rel = rel_data["label"]
            speaker = rel_data["speaker"]
            tr2sp[(subj, rel, obj)] = speaker

        for triplet in sample["triplets"]:
            if len(triplet) > 3 and triplet[-4] in ["pos", "neg", "neu"] and triplet[-2]:
                subj = triplet[-3]
                rel = triplet[-1]
                obj = triplet[-2]
                sent = triplet[-4]
                speaker = tr2sp.get((subj, rel, obj), "")
                if len(rel) > 1 and not rel[0].isdigit() and speaker and speaker != "Unidentified":
                    total_triplets.append([subj, rel, obj, sent, speaker])

print("triplets", len(total_triplets))
for element in total_triplets[:10]:
    print(element)

devices_set = set()
sp2device = {}
for device, opinion, feature, sentiment, speaker in total_triplets:
    if speaker not in sp2device:
        sp2device[speaker] = []
    if device not in sp2device[speaker]:
        sp2device[speaker].append(device)
    devices_set.add(device)

print("speakers", len(sp2device))

pos_samples, neg_samples = [], []
for speaker1 in sp2device:
    for speaker2 in sp2device:
        if speaker1 != speaker2:
            devices1 = sp2device[speaker1]
            devices2 = sp2device[speaker2]
            c_devices = list(set(devices1).intersection(set(devices2)))
            if c_devices:
                pos_samples.append([speaker1, speaker2, c_devices])
            else:
                neg_samples.append([speaker1, speaker2, c_devices])

random.shuffle(pos_samples)
random.shuffle(neg_samples)

questions = []
print("positive", len(pos_samples), "negative", len(neg_samples))
for speaker1, speaker2, c_devices in pos_samples[:200] + neg_samples[:200]:
    question = f"Do {speaker1} and {speaker2} use the same device models?"
    if c_devices:
        answer = ", ".join(c_devices)
    else:
        answer = "No"
    questions.append({"question": question, "answer": answer})

random.shuffle(questions)
with open("same_devices.json", 'w') as out:
    json.dump(questions, out, indent=2)

with open("devices.txt", 'w') as out:
    for device in devices_set:
        out.write(device+'\n')

manf_dict = {"Xiaomi": "Xiaomi", "Apple": "Apple", "OnePlus": "OnePlus", "Vivo": "Vivo", "Honor": "Honor",
             "Huawei": "Huawei", "Samsung": "Samsung", "Redmi": "Xiaomi", "Iphone": "Apple", "One Plus": "OnePlus"}
pos_samples, neg_samples = [], []
for speaker1 in sp2device:
    for speaker2 in sp2device:
        if speaker1 != speaker2:
            devices1 = sp2device[speaker1]
            devices2 = sp2device[speaker2]
            manf1, manf2 = [], []
            for device in devices1:
                for manf in manf_dict:
                    if device.lower() == manf.lower():
                        manf1.append(manf_dict[manf])
                    elif any([tok == manf.lower() for tok in device.lower().split()]):
                        manf1.append(manf_dict[manf])

            for device in devices2:
                for manf in manf_dict:
                    if device.lower() == manf.lower():
                        manf2.append(manf_dict[manf])
                    elif any([tok == manf.lower() for tok in device.lower().split()]):
                        manf2.append(manf_dict[manf])
            common_manf = list(set(manf1).intersection(set(manf2)))
            if common_manf:
                pos_samples.append([speaker1, speaker2, common_manf])
            else:
                neg_samples.append([speaker1, speaker2, common_manf])

print("positive", len(pos_samples), "negative", len(neg_samples))

random.shuffle(pos_samples)
random.shuffle(neg_samples)

questions = []
for speaker1, speaker2, c_manf in pos_samples[:200] + neg_samples[:200]:
    question = f"Do {speaker1} and {speaker2} prefer the same device manufacturer?"
    if c_manf:
        answer = ", ".join(c_manf)
    else:
        answer = "No"
    questions.append({"question": question, "answer": answer})

random.shuffle(questions)
with open("same_manufacturer.json", 'w') as out:
    json.dump(questions, out, indent=2)

tr2sp = {}
for device, opinion, feature, sentiment, speaker in total_triplets:
    if sentiment.lower() in ["positive", "negative"]:
        if (device, sentiment, feature):
            tr2sp[(device, sentiment, feature)] = []
        if speaker not in tr2sp[(device, sentiment, feature)]:
            tr2sp[(device, sentiment, feature)].append(speaker)

questions = []
for (device, sentiment, feature), speakers in tr2sp.items():
    question = f"Which people have {sentiment} opinion about {feature} if {device}?"
    answer = ", ".join(speakers)
    questions.append({"question": question, "answer": answer})

with open("which_people_about_device.json", 'w') as out:
    json.dump(questions[:400], out, indent=2)

sp2tr = {}
for device, opinion, feature, sentiment, speaker in total_triplets:
    manf = ""
    for c_manf in manf_dict:
        if device.lower() == c_manf.lower():
            manf = manf_dict[c_manf]
        elif any([tok == c_manf.lower() for tok in device.lower().split()]):
            manf = manf_dict[c_manf]
    if manf:
        if speaker not in sp2tr:
            sp2tr[speaker] = []
        if (manf, sentiment, feature) not in sp2tr[speaker]:
            sp2tr[speaker].append((manf, sentiment, feature))

questions = []
for speaker1 in sp2tr:
    for speaker2 in sp2tr:
        if speaker1 != speaker2 and sp2tr[speaker1] == sp2tr[speaker2]:
            question = f"Whose opinions about manufacturers are most similar to {speaker1}'s?"
            answer = speaker2
            questions.append({"question": question, "answer": answer})
            print("-----", speaker1, speaker2, sp2tr[speaker1])

with open("similar_opinions.json", 'w') as out:
    json.dump(questions, out, indent=2)

print("questions", len(questions))