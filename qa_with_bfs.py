import json
import os
import pickle
import transformers
import torch
from retrieve.retriever import Retriever
from neo4j_functions import Neo4jConnection

retriever = Retriever(device="cuda")
print("retriever loaded")

if os.path.exists("triplet_embs.pickle"):
    with open("triplet_embs.pickle", 'rb') as inp:
        triplet_embs_dict = pickle.load(inp)
else:
    with open("total_triplets.json", 'r') as inp:
        total_triplets = json.load(inp)

    triplet_str_list = []
    triplet_keys_list = []
    for subj, rel, obj, rel_data in total_triplets:
        subj_str = ", ".join([f"{key}: {value}" for key, value in subj.items()])
        obj_str = ", ".join([f"{key}: {value}" for key, value in obj.items()])
        rel_data_items = list(rel_data.items())
        rel_data_items = [(key, value) for key, value in rel_data_items
                          if key not in ["raw_time", "time", "sentiment"]]
        rel_data_items = sorted(rel_data_items, key=lambda x: x[0])
        rel_data_values = [element[1].lower() for element in rel_data_items]
        rel_data_str = ", ".join([f"{key}: {value}" for key, value in rel_data_items])
        triplet_str = f"{subj_str}, {rel}, {obj_str}, {rel_data_str}"
        subj_values = [val.lower() for val in subj.values()]
        obj_values = [val.lower() for val in obj.values()]
        keys = subj_values + [rel] + obj_values + rel_data_values
        triplet_keys_list.append(tuple(keys))
        triplet_str_list.append(triplet_str)

    print("triplet_keys_list", len(triplet_keys_list), "triplet_str_list", len(triplet_str_list))
    with open("triplet_keys.txt", 'w') as out:
        for keys, triplet_str in zip(triplet_keys_list, triplet_str_list):
            out.write(f"{keys} --- {triplet_str}"+'\n')
        for keys, triplet_str in zip(triplet_keys_list[-10:], triplet_str_list[-10:]):
            out.write(f"{keys} --- {triplet_str}"+'\n')

    triplet_embs_dict = {}
    chunk_size = 1000
    num_chunks = len(triplet_str_list) // chunk_size + int(len(triplet_str_list) % chunk_size > 0)
    for i in range(num_chunks):
        keys_chunk = triplet_keys_list[i*chunk_size:(i+1)*chunk_size]
        str_chunk = triplet_str_list[i*chunk_size:(i+1)*chunk_size]
        embs_chunk = retriever.embed(str_chunk)
        embs_chunk = embs_chunk.cpu().numpy()
        for keys, emb in zip(keys_chunk, embs_chunk):
            triplet_embs_dict[keys] = emb
        print("embs iter", i)

    with open("triplet_embs.pickle", 'wb') as out:
        pickle.dump(triplet_embs_dict, out)

conn = Neo4jConnection(uri="bolt://31.207.47.254:7687", user="neo4j", pwd="password", embs_dict=triplet_embs_dict)

use_embs = False
if use_embs:
    with open("entities.json", 'r') as inp:
        entities_vocab = json.load(inp)

    entities_dict = {}
    for entity, e_type in entities_vocab:
        if e_type not in entities_dict:
            entities_dict[e_type] = []
        entities_dict[e_type].append(entity.replace("_", " "))

    emb_dict = {}
    for e_type, entities in entities_dict.items():
        print(e_type, f"number of entities: {len(entities)}", entities[:5])
        embs = retriever.embed(entities)
        emb_dict[e_type] = embs

    query = ["take photos"]
    query_embs = retriever.embed(query)
    result = retriever.search_in_embeds(emb_dict["feature"], query_embs, 5)
    print("result", result)

model_name = "Undi95/Meta-Llama-3-8B-Instruct-hf"

pipeline = transformers.pipeline(
    "text-generation",
    model=model_name,
    model_kwargs={"torch_dtype": torch.bfloat16},
    device_map="auto",
    max_new_tokens=200
)

def process_chain(chain, chain_subj_obj, chain_triplets):
    for triplet in chain:
        subj = triplet[0].items()
        subj = sorted(subj, key=lambda x: x[1])
        obj = triplet[-2].items()
        obj = sorted(obj, key=lambda x: x[1])
        subj = str(subj)
        obj = str(obj)
        rel_props = triplet[2].items()
        rel_props = [(key, value) for key, value in rel_props if key not in ["raw_time", "time"]]
        rel_props = sorted(rel_props, key=lambda x: x[0])
        rel_props = str(rel_props)
        if (subj, obj, rel_props) not in chain_subj_obj and (obj, subj, rel_props) not in chain_subj_obj \
                and triplet not in chain_triplets:
            chain_triplets.append(triplet)
            chain_subj_obj.add((subj, obj, rel_props))
    return chain_subj_obj, chain_triplets


def process_inters_chains1(inters_chains1):
    chain_triplets1 = []
    chain_subj_obj1 = set()
    for chain in inters_chains1:
        chain_subj_obj1, chain_triplets1 = process_chain(chain, chain_subj_obj1, chain_triplets1)
    return chain_triplets1


def process_inters_chains2(inters_chains2):
    chain_triplets2 = []
    chain_subj_obj2 = set()
    for chain1, chain2, *_ in inters_chains2:
        chain_subj_obj2, chain_triplets2 = process_chain(chain1, chain_subj_obj2, chain_triplets2)
        chain_subj_obj2, chain_triplets2 = process_chain(chain2, chain_subj_obj2, chain_triplets2)
    return chain_triplets2


prompt_extract_template = """Extract entities (names and surnames, device names, features) from the question and define the types of entities ("person", "device", "feature").
Features are different technical characteristics of devices such as battery life, camera, display, accumulator, etc.
Question 1: Kayla has positive, negative or neutral opinion about video of Xiaomi 10Pro?
Entities 1: {{"Kayla": "person", "video": "feature", "Xiaomi 10Pro": "device"}}
Question 2: Which device is better in battery life: Apple or k30u?
Entities 2: {{"battery life": "feature", "Apple": "device", "k30u": "device"}}
Question 3: The majority of speakers have positive, neutral or negative sentiment about screen of Samsung?
Entities 3: {{"screen": "feature", "Samsung": "device"}}
Question 4: {question}
Entities 4: """

in_context_examples = [
    {"question": "Whose opinions from Anthony and Grace about devices are most similar to Faith's?",
     "info": """person: Anthony, device: Xiaomi, opinion: hard, feature: maintenance point
person: Anthony, device: mate30pro, opinion: not as good as, feature: signal
person: Anthony, device: iPhone, opinion: not as good as, feature: signal
person: Grace, device: Xiaomi 12, opinion: beat, feature: charging speed
person: Faith, device: Xiaomi, opinion: problem, feature: product control
person: Faith, device: k30s, opinion: not as good, feature: film effect
person: Faith, device: red rice, opinion: not as good, feature: film effect""",
     "chain of thought": """The task is to compare Anthony's and Grace's opinions to Faith's opinions about devices. Faith has two types of opinions: "problem" with the Xiaomi device and "not as good" with both k30s and red rice devices. We will look for similar expressions of dissatisfaction from Anthony and Grace. Grace's opinion about Xiaomi 12 is "beat," which is not similar to any of Faith's negative opinions. Anthony's opinions include "hard" for Xiaomi and "not as good as" for mate30pro and iPhone with respect to the signal feature. "Not as good as" matches Faith's "not as good."
     """,
     "final answer": "Anthony"
     },
    {"question": "The majority of speakers have positive, neutral or negative sentiment about signal of Apple?",
     "info": """person: Jessica, time: 25.11.2020, opinion: is okay, device: Apple, feature: signal
person: Bernard, time: 25.11.2020, opinion: No lag, device: Apple, feature: play games""",
     "chain of thought": """To determine the sentiment about the signal of Apple, we need to find the opinions specifically related to the "signal" feature of Apple. Opinion "Is okay" or "okay" denotes positive (not neutral) sentiment. From the provided info, only Jessica's opinion mentions the signal: "is okay" This is a positive sentiment. Since there's only one opinion regarding the signal, the majority sentiment is positive.""",
     "final answer": "Positive"
     },
    {"question": "Whose opinions from Rita and Bruce about devices are most similar to Danielle's?",
     "info": """person: Danielle, time: 15.11.2020, opinion: nice, device: Apple, feature: battery life
person: Rita, time: 30.12.2020, opinion: good, device: Apple, feature: battery life
person: Bruce, time: 30.12.2020, opinion: bad, device: Apple, feature: battery life""",
     "chain of thought": "Danielle and Rita both have positive opinions about the battery life feature of Apple devices, while Bruce has a negative opinion.",
     "final answer": "Rita"
     },
    {"question": "Whose opinions from Zachary and Hannah about devices are most similar to Oswald's?",
     "info": """person: Oswald, time: 15.11.2020, opinion: nice, device: Xiaomi, feature: battery life
person: Zachary, time: 30.12.2020, opinion: good, device: Nokia, feature: battery life
person: Hannah, time: 30.12.2020, opinion: bad, device: Apple, feature: battery life""",
     "chain of thought": "Our task is to indicate one person in the answer: Zachary or Hannah. one person: Zachary or Hannah. Zachary, Hannah and Oswald do not have common devices, but I can guess that Zachary's opinion can be more similar to Oswald's.",
     "final answer": "Zachary"
     },
    {"question": "Do Abraham and Violet prefer the same device manufacturer? If so, list common manufacturers. Otherwise, answer 'No'.",
     "info": """person: Abraham, has device, Redmi Note
device: Redmi Note, person: Violet, time: 29.12.2018, opinion: well, feature: take_pictures
device: Redmi Note, has device, person: Violet
person: Abraham, has device, 12pro
device: 12pro, manufacturer, OnePlus
person: Violet, has device, 12pro
manufacturer: Xiaomi, manufacturer, device: Redmi Note""",
     "chain of thought": "Both Abraham and Violet have devices manufactured by Xiaomi (Redmi Note) and OnePlus (12pro).",
     "final answer": "Xiaomi, OnePlus"
     },
    {"question": "Whose opinions from Gabriella and Arianna about manufacturers are most similar to Alexandra's?",
     "info": """person: Gabriella, has device, device: Apple
person: Alexandra, time: 10.11.2020, Runs out quickly, device: Apple, feature: battery life
device: Apple, has device, person: Alexandra
person: Alexandra, has device, device: Apple
person: Gabriella, has device, device: Apple
device: Apple, manufacturer, manufacturer: Apple
manufacturer: Apple, manufacturer, device: iPhone
manufacturer: Apple, manufacturer, device: apple
manufacturer: Apple, manufacturer, device: iphone
manufacturer: Apple, manufacturer, device: IPHONE""",
     "chain of thought": "Our task is to indicate one person in the answer: Gabriella or Arianna. We should not search completely matching opinions of two people, instead we should define who of two people: Gabriella or Arianna is a little closer in opinions about devices to Alexandra. So, let's think about it. Both Gabriella and Alexandra use Apple devices and Arianna opinions are not mentioned. Therefore, Gabriella's opinions about manufacturers are more similar to Alexandra's.",
     "final answer": "Gabriella"
     },
    {"question": "The majority of speakers have positive, neutral or negative sentiment about display of Mi 10?",
     "info": "person: Alan, time: 10.9.2020, Colors are vibrant, feature: screen, device: Mi 10",
     "chain of thought": "The sentiment about the display of Mi 10 is positive according to Alan's statement that the colors are vibrant. There is no mention of any negative or neutral comments about the display.",
     "final answer": "Positive"
    },
    {"question": "The majority of speakers have positive, neutral or negative sentiment about video of LG?",
     "info": "",
     "chain of thought": "If info is provided, we suppose positive sentiment.",
     "final answer": "Positive"
    },
    {"question": "What Miles's opinion (positive, negative or neutral) about quality of MIX was dominant during using MIX?",
     "info": """person: miles, has device, device: mix
person: Miles, time: 25.12.2018, just alright, feature: quality, device: mix
person: Miles, time: 26.9.2020, camera is amazing, device: mix, feature: photo""",
     "chain of thought": """There is only one provided opinion about the quality feature of the MIX device. On 25.12.2018, Miles described the quality as "just alright," which indicates a neutral stance rather than a positive or negative one.""",
     "final answer": "Neutral"
    },
    {"question": "What Megan's opinion (positive, negative or neutral) about system of GT was dominant during using GT?",
     "info": """person: Megan, time: 20.12.2020, so userfriendly, feature: system, device: gt
person: Megan, time: 5.12.2020, its been freezing, feature: system, device: gt
person: Megan, time: 18.11.2020, quite stable, feature: system, device: gt
person: megan, has device, device: gt
person: Andrew, time: 27.10.2020, so smooth, feature: system, device: gt
person: Andrew, time: 20.12.2020, really smooth, feature: system, device: gt
person: Cody, time: 19.9.2020, too buggy, feature: system, device: xiaomi""",
     "chain of thought": """Reviewing all the provided information about Megan's opinions, we see that on 20.12.2020 she found the system user-friendly, on 5.12.2020 she mentioned it was freezing, and on 18.11.2020 she found it stable. There are mixed reviews, but she did express a positive opinion about its user-friendliness after expressing a negative view about the freezing issue. The most dominant feedback is positive.""",
     "final answer": "Positive"
    },
    {"question": "What opinion (positive, negative or neutral) about screen of Xiaomi was last during Ashton's experience of Xiaomi?",
     "info": """person: Ashton, time: 24.11.2020, doesnt live, feature: screen, device: xiaomi
person: ashton, has device, device: xiaomi
person: Grace, time: 23.11.2020, really subpar screen, feature: screen, device: xiaomi
person: Delia, time: 17.12.2020, amazing screen quality, feature: screen, device: xiaomi""",
     "chain of thought": """There is only one Ashton's opinion on 24.11.2020 ("doesnt live") about screen of Xiaomi, which is negative ("doesnt live" means that the screen does not work).""",
     "final answer": "Negative"
    }
]

prompt_similar_template = """Sort the phrases list in descending order of similarity to the phrase "{phrase}" from the sentence "{sentence}". Give the answer in the format: 1. ... , 2. ... , etc.
Phrases list: {phrases_list}
Sorted phrases list: """

prompt_answer_template = """Answer the question, based on provided info by analogy with examples given. Avoid giving None final answer, if you are not sure, give a guess answer. None answers are strictly prohibited. Generate chain of thought and then give the final answer in the following format:
### Answer
Chain of thought: ... Final answer: ...
{examples}
Question {n}: {question}
Info {n}: {info}
### Answer {n} """

in_context_questions = [element["question"] for element in in_context_examples]
in_cont_embs = retriever.embed(in_context_questions)

num_in_cont = 3

for flname, depth in [
        #["compare_questions.json", 1],
        #["compare_sentiment.json", 1],
        #["compare_sentiment_synonims.json", 1],
        #["device_sentiment.json", 1],
        #["same_devices.json", 1],
        ["same_manufacturer.json", 2]
        #["similar_device_opinions.json", 2],
        #["similar_manf_opinions.json", 2],
        #["which_people_about_device.json", 1],
        #["which_people_about_device_synonims.json", 1],
        #["dominant_opinion.json", 1],
        #["last_opinion.json", 1]
    ]:
    with open(f"questions/{flname}", 'r') as inp:
        dataset = json.load(inp)
    if depth == 1:
        thres1 = 8
        thres2 = 4
    elif depth > 1:
        thres1 = 6
        thres2 = 3
    results = []
    for nq, element in enumerate(dataset[:20]):
        question = element["question"]
        answer = element["answer"]
        print(f"{nq} --- question: {question}")
        print(f"answer: {answer}")

        query = [question]
        query_embs = retriever.embed(query)
        result = retriever.search_in_embeds(in_cont_embs, query_embs, 5)
        idx = result["idx"][0][:num_in_cont]
        retr_questions = [in_context_questions[ind] for ind in idx]
        retr_in_cont_examples = [in_context_examples[ind] for ind in idx]

        prompt = prompt_extract_template.format(question=question)
        res = pipeline(prompt)
        raw_entities = res[0]["generated_text"].split(prompt)[-1].split("\n")[0].strip()
        entities = {}
        try:
            entities = json.loads(raw_entities)
        except Exception as e:
            print(f"error: {e}")
        with open("qa_bfs_log.txt", 'a') as out:
            out.write(f"{nq} question: {question}"+'\n')
            out.write(f"answer: {answer}"+'\n')
            out.write(f"entities: {entities}"+'\n')
            out.write(f"retr_questions: {retr_questions}"+'\n')
        triplets_formatted = []
        entities_input = []
        for entity, tp in entities.items():
            cur_entities_input = [(entity, "", "node")]
            if use_embs and tp in emb_dict:
                query = [entity]
                query_embs = retriever.embed(query)
                result = retriever.search_in_embeds(emb_dict[tp], query_embs, 30)
                idx = result["idx"][0]
                retr_entities = [entities_dict[tp][ind] for ind in idx]
                sorted_entities_str = ""
                if tp == "device" and entity.lower() == retr_entities[0].lower():
                    pass
                else:
                    phrases_list = ", ".join(retr_entities)
                    prompt = prompt_similar_template.format(phrase=entity, sentence=question, phrases_list=phrases_list)
                    res = pipeline(prompt)
                    sorted_entities_str = res[0]["generated_text"].split(prompt)[-1].split("\n")[0]
                    if "1." in sorted_entities_str:
                        sorted_entities = sorted_entities_str.split(",")
                        sorted_entities = [" ".join(s_ent.split()[1:]).strip() for s_ent in sorted_entities]
                        for s_ent in sorted_entities[:3]:
                            if s_ent.lower() != entity.lower():
                                cur_entities_input.append((s_ent, "", "node"))
                    else:
                        for s_ent in retr_entities[:2]:
                            if s_ent.lower() != entity.lower():
                                cur_entities_input.append((s_ent, "", "node"))
                with open("qa_bfs_log.txt", 'a') as out:
                    out.write(f"retr_entities: {retr_entities[:5]}"+'\n')
                    out.write(f"sorted_entities: {sorted_entities_str}"+'\n')
                    out.write(f"cur_entities_input: {cur_entities_input}"+'\n')
            if cur_entities_input not in entities_input:
                entities_input.append(cur_entities_input)
            print("input_entities", cur_entities_input)
        with open("qa_bfs_log.txt", 'a') as out:
            out.write(f"entities_input: {entities_input}"+'\n')

        triplets_dict, inters_chains1, inters_chains2 = conn.bfs(
            entities_input, depth, question=question, retriever=retriever, db="testdb"
        )
        inters_chains1 = sorted(inters_chains1, key=lambda x: x[1], reverse=True)
        inters_chains1_more = [ch for ch, cnt in inters_chains1 if cnt > 1]
        inters_chains1_less = [ch for ch, cnt in inters_chains1 if cnt == 1]
        chain_triplets1_more = process_inters_chains1(inters_chains1_more)
        chain_triplets1_less = process_inters_chains1(inters_chains1_less)
        chain_triplets2 = process_inters_chains2(inters_chains2)
        prob_tr = False
        if inters_chains1_more:
            chain_triplets = chain_triplets1_more + chain_triplets1_less[:3] + chain_triplets2[:3]
            prob_tr = True
        else:
            chain_triplets = chain_triplets1_less + chain_triplets2

        def format_triplet(triplet):
            formatted_triplet = ""
            subj, rel, rel_props, obj, *_ = triplet
            subj = {key.replace("_", " "): value.replace("_", " ") for key, value in subj.items()}
            obj = {key.replace("_", " "): value.replace("_", " ") for key, value in obj.items()}
            rel = rel.replace("_", " ")
            rel_props = {key.replace("_", " "): value.replace("_", " ") for key, value in rel_props.items()}
            subj_str = ", ".join([f"{key}: {value}" for key, value in subj.items()])
            obj_str = ", ".join([f"{key}: {value}" for key, value in obj.items()])
            if rel_props:
                rel_props_list = []
                for key, value in rel_props.items():
                    if key in rel:
                        rel_props_list.append(value)
                    else:
                        rel_props_list.append(f"{key}: {value}")
                rel_props_str = ", ".join(rel_props_list)
                formatted_triplet = f"{rel_props_str}, {subj_str}, {obj_str}"
            else:
                formatted_triplet = f"{subj_str}, {rel}, {obj_str}"
            return formatted_triplet

        for triplet in chain_triplets[:25]:
            formatted_triplet = format_triplet(triplet)
            triplets_formatted.append(formatted_triplet)

        if chain_triplets:
            thres = thres2
        else:
            thres = thres1
        if len(chain_triplets) < 20 and not prob_tr:
            total_f_triplets = []
            for (step, direction, seed_entity, rel), triplets in triplets_dict.items():
                f_triplets = []
                for triplet in triplets:
                    reverse_triplet = [triplet[-1]] + triplet[1:-1] + [triplet[0]]
                    if triplet not in total_f_triplets and reverse_triplet not in total_f_triplets:
                        f_triplets.append(triplet)
                        total_f_triplets.append(triplet)
                for triplet in f_triplets[:thres]:
                    formatted_triplet = format_triplet(triplet)
                    triplets_formatted.append(formatted_triplet)

        triplets_str = "\n".join(triplets_formatted)
        with open("qa_bfs_log.txt", 'a') as out:
            out.write(f"triplets: {triplets_str}"+'\n\n')

        in_cont_str_list = []
        for nc, in_cont_element in enumerate(retr_in_cont_examples):
            in_cont_question = in_cont_element["question"].strip()
            info = in_cont_element["info"].strip()
            chain_of_thought = in_cont_element["chain of thought"].strip()
            final_answer = in_cont_element["final answer"].strip()
            e_num = nc + 1
            in_cont_str = f"""Question {e_num}: {in_cont_question}
Info {e_num}: {info}
### Answer {e_num}
Chain of thought {e_num}: {chain_of_thought}
Final answer {e_num}: {final_answer}"""
            in_cont_str_list.append(in_cont_str)
        in_cont_examples_str = "\n".join(in_cont_str_list)

        prompt = prompt_answer_template.format(examples=in_cont_examples_str, n=num_in_cont+1, question=question, info=triplets_str)
        #with open("qa_bfs_log.txt", 'a') as out:
        #    out.write(f"prompt: {prompt}"+'\n\n')
        res = pipeline(prompt)

        res_init = res[0]["generated_text"]
        res = res_init.split(prompt)[-1]
        pred_answer = ""
        found_line = ""
        for line in res.split("\n"):
            if f"Final answer {num_in_cont}" in line:
                found_line = line
                break
        if not found_line and f"Final answer {num_in_cont + 1}" in res:
            fnd = res.find(f"Final answer {num_in_cont + 1}")
            found_line = res[fnd:]

        with open("qa_bfs_log.txt", 'a') as out:
            out.write(f"found_line: {found_line}"+'\n\n')

        if found_line:
            pred_answer = found_line.split(f"Final answer {num_in_cont + 1}: ")[-1]
        elif len(res.split("\n")) > 1:
            pred_answer = res.split("\n")[1]
        else:
            pred_answer = ""
        pred_answer = pred_answer.split(f"Question {num_in_cont + 2}")[0]
        with open("qa_bfs_log.txt", 'a') as out:
            out.write(f"pred_answer: {pred_answer}"+'\n')
            out.write(f"res_answer: {res}"+'\n')
            out.write("_"*70+'\n\n')

        print("pred_answer", pred_answer)
        results.append({"question": question, "triplets": triplets_formatted, "gold_answer": answer, "pred_answer": pred_answer})
        if use_embs:
            with open(f"answers/{flname.replace('.json', '')}_bfs_emb.json", 'w') as out:
                json.dump(results, out, indent=2)
        else:
            with open(f"answers/{flname.replace('.json', '')}_bfs.json", 'w') as out:
                json.dump(results, out, indent=2)