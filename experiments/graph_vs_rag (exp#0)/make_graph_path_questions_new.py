import json
import random

random.seed(1)

with open("Augment_DiaASQ.json", 'r') as inp:
    data = json.load(inp)
samples = [element for element in data["data"] if "_" not in element.get("doc_id", "")]

total_triplets = []
for sample in samples:
    triplets = sample["clean_triplets"]
    speakers = sample["speakers"]
    if "speakers_names" in sample:
        speakers_names = sample["speakers_names"]
    else:
        speakers_names = sample["speakers"]
    for triplet in triplets:
        subj, obj, rel_data = triplet
        rel = rel_data["label"]
        speaker = rel_data["speaker"]
        sent = rel_data["sentiment"]
        time = rel_data["time"]
        if len(rel) > 1 and not rel[0].isdigit() and speaker and len(speaker.split()) == 1 \
                and speaker.lower() != "unidentified" and speaker in speakers_names:
            total_triplets.append([subj, rel, obj, sent, speaker, time])

print("triplets", len(total_triplets))
for element in total_triplets[:10]:
    print(element)

devices_set = set()
sp2device = {}
for device, opinion, feature, sentiment, speaker, time in total_triplets:
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
    question = f"Do {speaker1} and {speaker2} have any common devices (which {speaker1} and {speaker2} both use)? " + \
        "If so, list common devices. Otherwise, answer 'No'."
    if c_devices:
        answer = ", ".join(c_devices)
    else:
        answer = "No"
    questions.append({"question": question, "answer": answer})

random.shuffle(questions)
with open("questions/same_devices.json", 'w') as out:
    json.dump(questions[:200], out, indent=2)

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
    question = f"Do {speaker1} and {speaker2} prefer the same device manufacturer? " + \
        "If so, list common manufacturers. Otherwise, answer 'No'."
    if c_manf:
        answer = ", ".join(c_manf)
    else:
        answer = "No"
    questions.append({"question": question, "answer": answer})

random.shuffle(questions)
with open("questions/same_manufacturer.json", 'w') as out:
    json.dump(questions[:200], out, indent=2)

tr2sp = {}
for device, opinion, feature, sentiment, speaker, time in total_triplets:
    time = time.split(",")[0]
    if sentiment.lower() in ["positive", "negative", "pos", "neg"]:
        if (device, sentiment, feature, time) not in tr2sp:
            tr2sp[(device, sentiment, feature, time)] = []
        if speaker not in tr2sp[(device, sentiment, feature, time)]:
            tr2sp[(device, sentiment, feature, time)].append(speaker)

questions = []
for (device, sentiment, feature, time), speakers in tr2sp.items():
    question = f"Which people have {sentiment} opinion about {feature} of {device} on {time}?"
    question = question.replace("neg", "negative").replace("pos", "positive")
    answer = ", ".join(speakers)
    questions.append({"question": question, "answer": answer})

with open("questions/which_people_about_device.json", 'w') as out:
    json.dump(questions[:400], out, indent=2)

sp2tr = {}
for device, opinion, feature, sentiment, speaker, time in total_triplets:
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
    inters_info = []
    for speaker2 in sp2tr:
        if speaker1 != speaker2:
            inters = set(sp2tr[speaker1]).intersection(set(sp2tr[speaker2]))
            inters_info.append([speaker2, len(inters)])
    inters_info = sorted(inters_info, key=lambda x: x[1], reverse=True)
    if inters_info[0][1] >= 0.32 * max(len(sp2tr[speaker1]), len(sp2tr[inters_info[0][0]])):
        question = f"Whose opinions from {inters_info[0][0]} and {inters_info[-1][0]} about " + \
            f"manufacturers are most similar to {speaker1}'s?"
        answer = inters_info[0][0]
        print(question, answer)
        questions.append({"question": question, "answer": answer})

# Whose opinions from speaker1, speaker2, speaker3 about manufacturers are most similar to speaker4's?

with open("questions/similar_manf_opinions.json", 'w') as out:
    json.dump(questions, out, indent=2)

print("questions", len(questions))

sp2tr = {}
for device, opinion, feature, sentiment, speaker, time in total_triplets:
    if speaker not in sp2tr:
        sp2tr[speaker] = []
    if (device, sentiment, feature) not in sp2tr[speaker]:
        sp2tr[speaker].append((device, sentiment))

print("----- sp2tr", len(sp2tr))
questions = []
for speaker1 in sp2tr:
    inters_info = []
    for speaker2 in sp2tr:
        if speaker1 != speaker2:
            inters = set(sp2tr[speaker1]).intersection(set(sp2tr[speaker2]))
            inters_info.append([speaker2, len(inters)])
    inters_info = sorted(inters_info, key=lambda x: x[1], reverse=True)
    print("inters_info", inters_info[0], round(0.2 * max(len(sp2tr[speaker1]), len(sp2tr[inters_info[0][0]])), 3))
    if inters_info[0][1] >= 0.2 * max(len(sp2tr[speaker1]), len(sp2tr[inters_info[0][0]])):
        question = f"Whose opinions from {inters_info[0][0]} and {inters_info[-1][0]} about " + \
            f"devices are most similar to {speaker1}'s?"
        answer = inters_info[0][0]
        print(question, answer)
        questions.append({"question": question, "answer": answer})

# Whose opinions from speaker1, speaker2, speaker3 about manufacturers are most similar to speaker4's?

with open("questions/similar_device_opinions.json", 'w') as out:
    json.dump(questions, out, indent=2)

print("questions", len(questions))