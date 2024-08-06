import json
import transformers
import torch
from neo4j_functions import Neo4jConnection

with open("same_devices.json", 'r') as inp:
    dataset = json.load(inp)

conn = Neo4jConnection(uri="bolt://31.207.47.254:7687", user="neo4j", pwd="password")

model_name = "Undi95/Meta-Llama-3-8B-Instruct-hf"

pipeline = transformers.pipeline(
    "text-generation",
    model=model_name,
    model_kwargs={"torch_dtype": torch.bfloat16},
    device_map="auto",
    max_new_tokens=200
)

prompt_extract = """Extract entities (names and surnames, device names, company names) from the question and define the types of entities ("person", "device", "manufacturer").
Question example: Kayla has positive, negative or neutral opinion about video of Xiaomi 10Pro?
Entities example: {{"Kayla": "person", "Xiaomi 10Pro": "device"}}
Question example: Which device is better in battery life: Apple or k30u?
Entities example: {{"Apple": "device", "k30u": "device"}}
Question: {question}
Entities: """

prompt_answer = """Answer the question, based on provided info by analogy with examples given.
Question example: Do Brianna and Joseph use the same device models?
Info example: sentiment: pos, person: Brianna, device: OnePlus, opinion: like most, feature: texture; sentiment: pos, person: Brianna, device: OnePlus 10PRO, opinion: more attractive, feature: screen; sentiment: neg, person: Joseph, device: Xiaomi, opinion: age faster, feature: battery; sentiment: neu, person: Joseph, device: 11u, opinion: not much difference, feature: taking pictures;
Answer example: No.
Question example: Do Justin and Isaac use the same device models?
Info example: sentiment: neg, person: Justin, device: xiaomi12Pro, opinion: lower, feature: temperature; sentiment: neu, person: Justin, device: xiaomi12Pro, opinion: same, feature: performance; sentiment: pos, person: Justin, device: OPPO vivo, opinion: good, feature: quality; sentiment: pos, person: Justin, device: Xiaomi, opinion: high, feature: playability; sentiment: pos, person: Isaac, device: Apple, opinion: Think too highly, feature: photos; sentiment: pos, person: Isaac, device: Xiaomi Mi 10 Extreme Edition, opinion: incomparable, feature: screen; sentiment: neg, person: Isaac, device: Xiaomi, opinion: not good, feature: quality control
Answer example: Xiaomi
Question: {question}
Info: {info}
Answer: """

for element in dataset:
    question = element["question"]
    answer = element["answer"]
    print(f"question: {question}")
    print(f"answer: {answer}")
    prompt = prompt_extract.format(question=question)
    res = pipeline(prompt)
    raw_entities = res[0]["generated_text"].split(prompt)[-1].split("\n")[0].strip()
    entities = json.loads(raw_entities)
    with open("qa_bfs_log.txt", 'a') as out:
        out.write(f"question: {question}"+'\n')
        out.write(f"answer: {answer}"+'\n')
        out.write(f"entities: {entities}"+'\n')
    triplets_formatted = []
    for entity, tp in entities.items():
        if tp == "person":
            triplets = conn.bfs(entity, prop_name="person", entity_type="rel_prop", subj_labels=["device"], db="testdb")
        else:
            triplets = conn.bfs(entity, db="testdb")
        for device, opinion, rel_props, feature in triplets:
            device = device.replace("_", " ")
            opinion = opinion.replace("_", " ")
            feature = feature.replace("_", " ")
            triplets_formatted.append(f"{rel_props}, device: {device}, opinion: {opinion}, feature: {feature}")
    triplets_str = "; ".join(triplets_formatted)
    with open("qa_bfs_log.txt", 'a') as out:
        out.write(f"triplets: {triplets_str}"+'\n')
        out.write("_"*60+'\n\n')

    prompt = prompt_answer.format(question=question, info=triplets_str)
    res = pipeline(prompt)
    pred_answer = res[0]["generated_text"].split(prompt)[-1].split("\n")[0].strip()
    print("pred_answer", pred_answer)