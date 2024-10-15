import json
import transformers
import torch
from retrieve.retriever import Retriever
from src.db_models.graph_db.neo4j_functions import Neo4jConnection

conn = Neo4jConnection(uri="bolt://31.207.47.254:7687", user="neo4j", pwd="password")

use_embs = True
if use_embs:
    retriever = Retriever(device="cuda")
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

prompt_extract_template = """Extract entities (names and surnames, device names, features, company names) from the question and define the types of entities ("person", "device", "manufacturer").
Question 1: Kayla has positive, negative or neutral opinion about video of Xiaomi 10Pro?
Entities 1: {{"Kayla": "person", "video": "feature", "Xiaomi 10Pro": "device"}}
Question 2: Which device is better in battery life: Apple or k30u?
Entities 2: {{"battery life": "feature", "Apple": "device", "k30u": "device"}}
Question 3: The majority of speakers have positive, neutral or negative sentiment about screen of Samsung?
Entities 3: {{"screen": "feature", "Samsung": "device"}}
Question 4: {question}
Entities 4: """

prompt_answer_template = """Answer the question, based on provided info by analogy with examples given. Generate chain of thought and then give the final answer in the following format:
### Answer
Chain of thought: ... Final answer: ...
Question 1: Whose opinions from Anthony and Grace about devices are most similar to Faith's?
Info 1: person: Anthony, device: Xiaomi, opinion: hard, feature: maintenance point
person: Anthony, device: mate30pro, opinion: not as good as, feature: signal
person: Anthony, device: iPhone, opinion: not as good as, feature: signal
person: Grace, device: Xiaomi 12, opinion: beat, feature: charging speed
person: Faith, device: Xiaomi, opinion: problem, feature: product control
person: Faith, device: k30s, opinion: not as good, feature: film effect
person: Faith, device: red rice, opinion: not as good, feature: film effect
### Answer 1
Chain of thought 1: The task is to compare Anthony's and Grace's opinions to Faith's opinions about devices. Faith has two types of opinions: "problem" with the Xiaomi device and "not as good" with both k30s and red rice devices. We will look for similar expressions of dissatisfaction from Anthony and Grace. Grace's opinion about Xiaomi 12 is "beat," which is not similar to any of Faith's negative opinions. Anthony's opinions include "hard" for Xiaomi and "not as good as" for mate30pro and iPhone with respect to the signal feature. "Not as good as" matches Faith's "not as good."
Final answer 1: Anthony
Question 2: The majority of speakers have positive, neutral or negative sentiment about signal of Apple?
Info 2: person: Alejandro, time: 15.11.2020, opinion: beats, device: Apple, feature: battery life
person: Jacqueline, time: 30.12.2020, opinion: Nice pictures taken, device: Apple, feature: taking pictures
person: Diego, time: 30.12.2020, opinion: Doesnt overheat, device: Apple, feature: heat radiation
person: Lily, time: 30.12.2020, opinion: Not bad, device: Apple, feature: configuration of other processors
person: Margaret, time: 25.11.2020, opinion: Pictures turn blurry, device: Apple, feature: taking pictures
person: Amber, time: 25.11.2020, opinion: Really unhelpful, device: Apple, feature: sales
person: Jessica, time: 25.11.2020, opinion: Always been strong, device: Apple, feature: signal
person: Bernard, time: 25.11.2020, opinion: No lag, device: Apple, feature: play games
### Answer 2
Chain of thought 2: To determine the sentiment about the signal of Apple, we need to find the opinions specifically related to the "signal" feature of Apple. From the provided info, only Jessica's opinion mentions the signal: "Always been strong." This is a positive sentiment. Since there's only one opinion regarding the signal, the majority sentiment is positive.
Final answer 2: Positive
Question 3: {question}
Info 3: {info}
### Answer 3 """


for flname, depth in [
        ["compare_questions.json", 1],
        ["compare_sentiment.json", 1],
        ["compare_sentiment_synonims.json", 1],
        ["device_sentiment.json", 1],
        ["same_devices.json", 1],
        ["same_manufacturer.json", 2],
        ["similar_device_opinions.json", 1],
        ["similar_manf_opinions.json", 2],
        ["which_people_about_device.json", 1],
        ["which_people_about_device_synonims.json", 1]
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
    for element in dataset[:10]:
        question = element["question"]
        answer = element["answer"]
        print(f"question: {question}")
        print(f"answer: {answer}")
        prompt = prompt_extract_template.format(question=question)
        res = pipeline(prompt)
        raw_entities = res[0]["generated_text"].split(prompt)[-1].split("\n")[0].strip()
        entities = {}
        try:
            entities = json.loads(raw_entities)
        except Exception as e:
            print(f"error: {e}")
        with open("qa_bfs_log.txt", 'a') as out:
            out.write(f"question: {question}"+'\n')
            out.write(f"answer: {answer}"+'\n')
            out.write(f"entities: {entities}"+'\n')
        triplets_formatted = []
        entities_input = []
        for entity, tp in entities.items():
            cur_entities_input = [(entity, "", "node")]
            if use_embs:
                query = [entity]
                query_embs = retriever.embed(query)
                result = retriever.search_in_embeds(emb_dict[tp], query_embs, 5)
                idx = result["idx"][0]
                retr_entities = [entities_dict[tp][ind] for ind in idx]
                if retr_entities[0].lower() != entity.lower():
                    cur_entities_input.append((retr_entities[0], "", "node"))
            entities_input.append(cur_entities_input)
            print("input_entities", cur_entities_input)

        triplets_dict, inters_chains = conn.bfs(entities_input, db="testdb")
        chain_triplets = []
        for chain in inters_chains:
            for triplet in chain:
                if triplet not in chain_triplets:
                    chain_triplets.append(triplet)

        def format_triplet(triplet):
            formatted_triplet = ""
            subj, rel, rel_props, obj = triplet
            subj = {key.replace("_", " "): value.replace("_", " ") for key, value in subj.items()}
            obj = {key.replace("_", " "): value.replace("_", " ") for key, value in obj.items()}
            rel_props = {key.replace("_", " "): value.replace("_", " ") for key, value in rel_props.items()}
            subj_str = ", ".join([f"{key}: {value}" for key, value in subj.items()])
            obj_str = ", ".join([f"{key}: {value}" for key, value in obj.items()])
            if rel_props:
                rel_props_str = ", ".join([f"{key}: {value}" for key, value in rel_props.items()])
                formatted_triplet = f"{rel_props_str}, {subj_str}, {obj_str}"
            else:
                formatted_triplet = f"{subj_str} {rel} {obj_str}"
            return formatted_triplet

        for triplet in chain_triplets[:12]:
            formatted_triplet = format_triplet(triplet)
            triplets_formatted.append(formatted_triplet)

        if chain_triplets:
            thres = thres2
        else:
            thres = thres1
        for (step, direction, rel), triplets in triplets_dict.items():
            for triplet in triplets[:thres]:
                formatted_triplet = format_triplet(triplet)
                triplets_formatted.append(formatted_triplet)

        triplets_str = "\n".join(triplets_formatted)
        with open("qa_bfs_log.txt", 'a') as out:
            out.write(f"triplets: {triplets_str}"+'\n\n')

        prompt = prompt_answer_template.format(question=question, info=triplets_str)
        res = pipeline(prompt)
        res = res[0]["generated_text"].split(prompt)[-1]
        pred_answer = ""
        found_line = ""
        for line in res.split("\n"):
            if "Final answer 3" in line:
                found_line = line
                break
        if found_line:
            pred_answer = found_line.split("Final answer 3: ")[-1]
        elif len(res.split("\n")) > 1:
            pred_answer = res.split("\n")[1]
        else:
            pred_answer = ""
        with open("qa_bfs_log.txt", 'a') as out:
            out.write(f"pred_answer: {res}"+'\n')
            out.write("_"*70+'\n\n')

        print("pred_answer", pred_answer)
        results.append({"question": question, "triplets": triplets_formatted, "gold_answer": answer, "pred_answer": pred_answer})
        with open(f"answers/{flname.replace('.json', '')}_bfs2.json", 'w') as out:
            json.dump(results, out, indent=2)