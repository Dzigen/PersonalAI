import json
import transformers
import torch
from src.db_models.graph_db.neo4j_functions import Neo4jConnection

conn = Neo4jConnection(uri="bolt://31.207.47.254:7687", user="neo4j", pwd="password")

model_name = "Undi95/Meta-Llama-3-8B-Instruct-hf"

pipeline = transformers.pipeline(
    "text-generation",
    model=model_name,
    model_kwargs={"torch_dtype": torch.bfloat16},
    device_map="auto",
    max_new_tokens=200
)

terminators = [
    pipeline.tokenizer.eos_token_id,
    pipeline.tokenizer.convert_tokens_to_ids("<|eot_id|>")
]

messages_extract = [
    {"role": "system", "content": """Extract entities (names and surnames, device names, company names) from the question and define the types of entities ("person", "device", "manufacturer")."""},
    {"role": "user", "content": "Question: Kayla has positive, negative or neutral opinion about video of Xiaomi 10Pro?"},
    {"role": "assistant", "content": """Entities: {"Kayla": "person", "Xiaomi 10Pro": "device"}"""},
    {"role": "user", "content": "Question: Which device is better in battery life: Apple or k30u?"},
    {"role": "assistant", "content": """Entities: {"Apple": "device", "k30u": "device"}"""},
    {"role": "user", "content": "Question: The majority of speakers have positive, neutral or negative sentiment about screen of Samsung?"},
    {"role": "assistant", "content": """Entities: {"Samsung": "device"}"""},
    {"role": "user", "content": "Question: {question}"}
]

messages_answer = [
    {"role": "system", "content": """Answer the question, based on provided info. Generate chain of thought and then give the final answer in the following format:
### Answer
Chain of thought: ... Final answer: ..."""},
    {"role": "user", "content": """Question: Whose opinions from Anthony and Grace about devices are most similar to Faith's?
Info: person: Anthony, device: Xiaomi, opinion: hard, feature: maintenance point
person: Anthony, device: mate30pro, opinion: not as good as, feature: signal
person: Anthony, device: iPhone, opinion: not as good as, feature: signal
person: Grace, device: Xiaomi 12, opinion: beat, feature: charging speed
person: Faith, device: Xiaomi, opinion: problem, feature: product control
person: Faith, device: k30s, opinion: not as good, feature: film effect
person: Faith, device: red rice, opinion: not as good, feature: film effect"""},
    {"role": "assistant", "content": """### Answer
Chain of thought: The task is to compare Anthony's and Grace's opinions to Faith's opinions about devices. Faith has two types of opinions: "problem" with the Xiaomi device and "not as good" with both k30s and red rice devices. We will look for similar expressions of dissatisfaction from Anthony and Grace. Grace's opinion about Xiaomi 12 is "beat," which is not similar to any of Faith's negative opinions. Anthony's opinions include "hard" for Xiaomi and "not as good as" for mate30pro and iPhone with respect to the signal feature. "Not as good as" matches Faith's "not as good."
Final answer: Anthony"""},
    {"role": "user", "content": """Question: The majority of speakers have positive, neutral or negative sentiment about signal of Apple?
Info: person: Alejandro, time: 15.11.2020, opinion: beats, device: Apple, feature: battery life
person: Jacqueline, time: 30.12.2020, opinion: Nice pictures taken, device: Apple, feature: taking pictures
person: Diego, time: 30.12.2020, opinion: Doesnt overheat, device: Apple, feature: heat radiation
person: Lily, time: 30.12.2020, opinion: Not bad, device: Apple, feature: configuration of other processors
person: Margaret, time: 25.11.2020, opinion: Pictures turn blurry, device: Apple, feature: taking pictures
person: Amber, time: 25.11.2020, opinion: Really unhelpful, device: Apple, feature: sales
person: Jessica, time: 25.11.2020, opinion: Always been strong, device: Apple, feature: signal
person: Bernard, time: 25.11.2020, opinion: No lag, device: Apple, feature: play games"""},
    {"role": "assistant", "content": """### Answer
Chain of thought: To determine the sentiment about the signal of Apple, we need to find the opinions specifically related to the "signal" feature of Apple. From the provided info, only Jessica's opinion mentions the signal: "Always been strong." This is a positive sentiment. Since there's only one opinion regarding the signal, the majority sentiment is positive.
Final answer: Positive"""},
    {"role": "user", "content": """Question: {question}
Info: {info}"""}
]

def generate(messages):
    prompt = pipeline.tokenizer.apply_chat_template(
        messages, 
        tokenize=False, 
        add_generation_prompt=True
    )
    outputs = pipeline(
        prompt,
        max_new_tokens=256,
        eos_token_id=terminators,
        do_sample=True,
        temperature=0.6,
        top_p=0.9,
    )
    return outputs[0]["generated_text"][len(prompt):]


for flname, depth in [
        #["compare_questions.json", 1],
        #["compare_sentiment.json", 1],
        #["device_sentiment.json", 1],
        #["same_devices.json", 1],
        #["same_manufacturer.json", 2],
        #["similar_device_opinions.json", 1],
        #["similar_manf_opinions.json", 2],
        ["which_people_about_device.json", 1]
    ]:
    with open(f"questions/{flname}", 'r') as inp:
        dataset = json.load(inp)
    if depth == 1:
        thres = 8
    elif depth > 1:
        thres = 6
    results = []
    for element in dataset[:10]:
        question = element["question"]
        answer = element["answer"]
        print(f"question: {question}")
        print(f"answer: {answer}")
        messages_extract[-1]["content"] = messages_extract[-1]["content"].format(question=question)
        res = generate(messages_extract)
        raw_entities = res.split("\n")[0].strip()
        print("raw_entities", raw_entities)
        raw_entities = raw_entities.split("Entities: ")[-1]
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
        for entity, tp in entities.items():
            if tp == "person":
                triplets_dict = conn.bfs(entity, prop_name="person", entity_type="rel_prop", subj_labels=["device"], db="testdb")
            else:
                triplets_dict = conn.bfs(entity, subj_labels=["device"], db="testdb")
            for (step, direction, rel), triplets in triplets_dict.items():
                for subj, rel, rel_props, obj in triplets[:thres]:
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

        triplets_str = "\n".join(triplets_formatted)
        with open("qa_bfs_log.txt", 'a') as out:
            out.write(f"triplets: {triplets_str}"+'\n\n')

        messages_answer[-1]["content"] = messages_answer[-1]["content"].format(question=question, info=triplets_str)
        res = generate(messages_answer)
        pred_answer = ""
        found_line = ""
        for line in res.split("\n"):
            if "Final answer" in line:
                found_line = line
                break
        if found_line:
            pred_answer = found_line.split("Final answer: ")[-1]
        else:
            pred_answer = res.split("\n")[1]
        with open("qa_bfs_log.txt", 'a') as out:
            out.write(f"pred_answer: {res}"+'\n')
            out.write("_"*70+'\n\n')

        print("pred_answer", pred_answer)
        results.append({"question": question, "triplets": triplets_formatted, "gold_answer": answer, "pred_answer": pred_answer})
        with open(f"answers/{flname}", 'w') as out:
            json.dump(results, out, indent=2)