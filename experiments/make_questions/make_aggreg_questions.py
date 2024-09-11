import json

with open("multiple_subjects.json", 'r') as inp:
    data = json.load(inp)

question_compare_template = "Which device is better in {feature}: {device1} or {device2}?"

questions1 = []
for obj, subj_rel_data in data:
    subj_rel_dict = {}
    for subj, rel, sent in subj_rel_data:
        if subj not in subj_rel_dict:
            subj_rel_dict[subj] = []
        subj_rel_dict[subj].append((rel, sent))
    subj_rel_list = list(subj_rel_dict.items())
    subj_rel_list = [element for element in subj_rel_list if len(element[1]) > 1]
    for subj1, rel_sent_data1 in subj_rel_list:
        for subj2, rel_sent_data2 in subj_rel_list:
            if subj1 != subj2:
                pos1, pos2, neg1, neg2 = 0, 0, 0, 0
                for rel, sent in rel_sent_data1:
                    if sent == "pos":
                        pos1 += 1
                    elif sent == "neg":
                        neg1 += 1
                for rel, sent in rel_sent_data2:
                    if sent == "pos":
                        pos2 += 1
                    if sent == "neg":
                        neg2 += 1
                if pos1 != pos2 and abs((pos1 - neg1) - (pos2 - neg2)) > 1 and abs((pos1 + neg1) - (pos2 + neg2)) < 3:
                    question = question_compare_template.format(feature=obj, device1=subj1, device2=subj2)
                    if pos1 > pos2:
                        answer = subj1
                    else:
                        answer = subj2
                    questions1.append({"question": question.replace("_", " "),
                                       "answer": answer.replace("_", " "),
                                       "type": "compare_questions"})

print("questions:", len(questions1))
for question in questions1[:5]:
    print(question["question"])

with open("questions/compare_questions.json", 'w') as out:
    json.dump(questions1[:200], out, indent=2)

with open("multiple_rels.json", 'r') as inp:
    data = json.load(inp)

question_sentiment_template = "The majority of speakers have positive, neutral or negative sentiment about {feature} of {device}?"

questions2 = []
for (subj, obj), rel_sent_data in data:
    sent_cnt_dict = {"pos": 0, "neu": 0, "neg": 0}
    for rel, sent in rel_sent_data:
        if sent in ["pos", "neg", "neu"]:
            sent_cnt_dict[sent] += 1
    if sent_cnt_dict["pos"] > sent_cnt_dict["neu"] or sent_cnt_dict["neu"] > sent_cnt_dict["neg"]:
        question = question_sentiment_template.format(feature=obj, device=subj)
        if sent_cnt_dict["pos"] > sent_cnt_dict["neu"] and sent_cnt_dict["pos"] > sent_cnt_dict["neg"]:
            answer = "Positive"
        elif sent_cnt_dict["neu"] > sent_cnt_dict["pos"] and sent_cnt_dict["neu"] > sent_cnt_dict["neg"]:
            answer = "Negative"
        elif sent_cnt_dict["neg"] > sent_cnt_dict["pos"] and sent_cnt_dict["neg"] > sent_cnt_dict["neu"]:
            answer = "Negative"
        questions2.append({"question": question.replace("_", " "),
                           "answer": answer.replace("_", " "),
                           "type": "compare_sentiment"})

print("questions:", len(questions2))
for question in questions2[:5]:
    print(question["question"])

with open("questions/compare_sentiment.json", 'w') as out:
    json.dump(questions2[:200], out, indent=2)