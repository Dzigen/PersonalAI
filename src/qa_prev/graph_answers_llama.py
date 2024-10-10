import json
import os
import re
import transformers
import torch
from src.db_models.graph_db.neo4j_functions import Neo4jConnection

os.environ['HF_HOME'] = '/archive/evseev.cache'

conn = Neo4jConnection(uri="bolt://31.207.47.254:7687", user="neo4j", pwd="password")

model_name = "Undi95/Meta-Llama-3-8B-Instruct-hf"

pipeline = transformers.pipeline(
    "text-generation",
    model=model_name,
    model_kwargs={"torch_dtype": torch.bfloat16},
    device_map="auto",
    max_new_tokens=200
)

PROMPT_TEMPLATES = {
    "subj_obj_person": """Generate Cypher query from the question by analogy with examples given.
Question example: Lily has positive, negative or neutral opinion about photography camera of XiaoMi 10pro?
Query example: MATCH (a)-[r]-(b) WHERE a.name="XiaoMi_10pro" AND b.name="photography_camera" AND r.person="Lily" RETURN a.name as device, r.person as person, type(r) as opinion, b.name as feature
Question: {question}
Query: """,
    "compare": """Generate Cypher query (or several queries, if necessary) from the question by analogy with examples given.
Question example: Which device is better in battery life: k30u or 13 promax?
Query example: MATCH (a)-[r]-(b) WHERE a.name="k30u" AND b.name="battery_life" RETURN a.name as device, r.person as person, type(r) as opinion, b.name as feature; MATCH (a)-[r]-(b) WHERE a.name="13_promax" AND b.name="battery_life" RETURN a.name as device, r.person as person, type(r) as opinion, b.name as feature
Question: {question}
Query: """,
    "subj_obj": """Generate Cypher query from the question by analogy with examples given.
The majority of speakers have positive, neutral or negative sentiment about video recording of One Plus?
Query example: MATCH (a)-[r]-(b) WHERE a.name="One_Plus" AND b.name="video_recording" RETURN a.name as device, r.person as person, type(r) as opinion, b.name as feature
Question: {question}
Query: """,
    "subj_person": """Generate Cypher query from the question by analogy with examples given.
Question example: What does Lily say about XiaoMi 10pro?
Query example: MATCH (a)-[r]-(b) WHERE a.name="XiaoMi_10pro" AND r.person="Lily" RETURN a.name as device, r.person as person, type(r) as opinion, b.name as feature
Question: {question}
Query: """
}

PROMPT_ANSWER = """Generate short answer to the question using information, extracted from the database.
Question example: Lily has positive, negative or neutral opinion about power of XiaoMi?
Information from the database example: 'device': 'XiaoMi', 'person': 'Lily', 'opinion': 'okay', 'feature': 'power'.
Answer example: Positive.
Question example: The majority of speakers have positive, neutral or negative sentiment about system of vivo?
Information from the database example: device: vivo, person: Laura, opinion: too_far, feature: system; device: vivo, person: Sofia, opinion: not_as_good_as, feature: system; device: vivo, person: Bernard, opinion: very_poor, feature: system; device: vivo, person: Bernard, opinion: vain, feature: system; device: vivo, person: Chase, opinion: very_smooth, feature: system; device: vivo, person: Chase, opinion: okay, feature: system
Answer example: Negative.
Question: {question}
Information from the database: {info}
Answer: """

PROMPT_ANSWER_COMPARE = """Generate the answer to the question using information, extracted from the database. The answer should be in the following form: first, summarize how many people have positive or negative opinion about each of the devices, and then give the final answer. If two devices have equal number of positive and negative opinions, make the decision which device is better based on the lexical form of opinions. Be sure to give the final answer.
Question example: Which device is better in battery life: 13mini or 13pro?
Information from the database example: device: 13mini, person: Jessica, opinion: improved a lot, feature: battery life; device: 13mini, person: Jesse, opinion: okay, feature: battery life; device: 13mini, person: Geoffrey, opinion: good, feature: battery life; device: 13pro, person: Taylor, opinion: better, feature: battery life; device: 13pro, person: Louis, opinion: ridiculously poor, feature: battery life
Answer example: about 13mini - 3 people have positive opinion. About 13pro - 1 man has positive opinion, 1 man has negative opinion. Final answer - 13mini.
Question: {question}
Information from the database: {info}
Answer: """

q_info = [
    #["questions_for_test.json", "subj_obj_person", "answers_simple.json", PROMPT_ANSWER],
    ["compare_questions.json", "compare", "answers_compare3.json", PROMPT_ANSWER_COMPARE]
    #["compare_sentiment.json", "subj_obj", "answers_sentiment.json", PROMPT_ANSWER]
]

for q_flname, pr_name, a_flname, prompt_template in q_info:
    with open(q_flname, 'r') as inp:
        questions = json.load(inp)
    qas = []
    for n, question_info in enumerate(questions[:200]):
        question = question_info["question"]
        print("question", question)
        gold_answer = question_info["answer"]
        try:
            prompt = PROMPT_TEMPLATES[pr_name].format(question=question)
            res = pipeline(prompt)
            queries_info = res[0]["generated_text"].split(prompt)[-1].split("\n")[0].strip()
            if ";" in queries_info:
                queries = queries_info.split(";")
                queries = [query.strip() for query in queries]
            else:
                queries = [queries_info.strip()]
            info = []
            for query in queries:
                entities = re.findall(r'(".*?")', query)
                for entity in entities:
                    entity_clean = entity.strip('"').replace("_", " ")
                    if entity_clean not in question and entity_clean.replace(" ", "") in question:
                        query = query.replace(entity.strip('"'), entity_clean.replace(" ", ""))
                res = conn.execute_query(query, db="testdb")
                print(f"query: {query} --- res: {res}")
                with open("graph_answers_log.txt", 'a') as out:
                    out.write(f"question: {question}"+'\n')
                    out.write(f"query: {query} --- res: {res}"+'\n\n')
                for element in res:
                    info_element = element.data()
                    info_element = [f"{key.replace('_', ' ')}: {value.replace('_', ' ')}"
                                    for key, value in info_element.items()]
                    info.append(", ".join(info_element))
            info_str = "; ".join(info)
            prompt = prompt_template.format(
                question=question,
                info=info_str
            )
            res = pipeline(prompt)
            with open("res_log.txt", 'a') as out:
                out.write(res[0]["generated_text"]+'\n\n')
            pred_answer = res[0]["generated_text"].split(prompt)[-1].split("Final answer")[1].split("\n")[0].strip()
            qas.append({"question": question,
                        "info": info_str,
                        "gold_answer": gold_answer,
                        "pred_answer": pred_answer
            })
            with open(a_flname, 'w') as out:
                json.dump(qas, out, indent=2)
            print("gold_answer", gold_answer)
            print("pred_answer", pred_answer)
            print("_"*60)
        except Exception as e:
            print(f"--- in: {question} --- error: {e}")

print("finished")