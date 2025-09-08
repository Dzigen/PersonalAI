import copy
import json
import os
import re
from neo4j_functions import Neo4jConnection
from retrieve.retriever import Retriever
from gigachat import GigaChat

CLIENT_SECRET = "cde75b76-43a3-45fa-a704-985d297d1a95"
AUTH_DATA = "Yzk4MTMzZDMtYjQzMy00Yjg0LWE5MzctNGU5YzEwMDhlNzA2OmNkZTc1Yjc2LTQzYTMtNDVmYS1hNzA0LTk4NWQyOTdkMWE5NQ=="
GIGACHAT_API = "YTMwNDM1NGMtNmMwZi00OGZjLTllNzctMmU0NmI3Y2JlNzRkOjVhNjU5ZjU0LTgzMjItNDhlZC1hMGQ4LWM2YjA1OTU3YzY5ZA=="

giga = GigaChat(credentials=AUTH_DATA, model="GigaChat-Pro",
                scope="GIGACHAT_API_PERS", verify_ssl_certs=False)

conn = Neo4jConnection(uri="bolt://31.207.47.254:7687",
                       user="neo4j", pwd="password")

retriever = Retriever(device="cuda")
print("retriever loaded")

prompt_query_templates = {
    "compare_questions": """Generate Cypher query (or several queries, if necessary) from the question by analogy with examples given.
Question example: Which device is better in battery life: k30u or 13 promax?
Query example: MATCH (a)-[r]-(b) WHERE a.name="k30u" AND b.name="battery_life" RETURN a.name as device, r.person as person, r.opinion as opinion, b.name as feature; MATCH (a)-[r]-(b) WHERE a.name="13_promax" AND b.name="battery_life" RETURN a.name as device, r.person as person, r.opinion as opinion, b.name as feature
Question: {question}
Query: """,
    "device_sentiment": """Generate Cypher query from the question by analogy with examples given.
Question example: Jessica has positive, negative or neutral opinion about fast charge of Xiaomi 10 on 22.12.2018?
Query example: MATCH (a)-[r]-(b) WHERE a.name="Xiaomi_10" AND b.name="fast_charge" AND r.person="Jessica" AND r.time="22.12.2018" RETURN a.name as device, r.person as person, r.opinion as opinion, b.name as feature
Question: {question}
Query: """,
    "compare_sentiment": """Generate Cypher query from the question by analogy with examples given.
Question example: The majority of speakers have positive, neutral or negative sentiment about video recording of One Plus?
Query example: MATCH (a)-[r]-(b) WHERE a.name="One_Plus" AND b.name="video_recording" RETURN a.name as device, r.person as person, r.opinion as opinion, b.name as feature
Question: {question}
Query: """,
    "same_devices": """Generate Cypher query from the question by analogy with examples given.
Question example: Do Jane and Jonathan have any common devices (which Jane and Jonathan both use)? If so, list common devices. Otherwise, answer 'No'.
Query example: MATCH (f1)<-[r1]-(d)-[r2]->(f2) WHERE r1.person="Jane" AND r2.person="Jonathan" RETURN r1.person as person1, d.name as device1, r2.person as person2, d.name as device2
Question: {question}
Query: """,
    "same_manufacturer": """Generate Cypher query from the question by analogy with examples given.
Question example: Do Aaliyah and Kathryn prefer the same device manufacturer?
Query example: MATCH (f1)<-[r1]-(d1)-[r3:manufacturer]->(m)<-[r4:manufacturer]-(d2)-[r2]->(f2) WHERE r1.person="Aaliyah" AND r2.person="Kathryn" RETURN r1.person as person1, d1.name as device1, m.name as manufacturer, d2.name as device2, r2.person as person2
Question: {question}
Query: """,
    "similar_device_opinions": """Generate Cypher query (or several queries, if necessary) from the question by analogy with examples given.
Question example: Whose opinions from Freda and Bruce about devices are most similar to Kayla's?
Query example: MATCH (a)-[r]-(b) WHERE r.person="Freda" RETURN a.name as device, r.person as person, r.opinion as opinion, b.name as feature; MATCH (a)-[r]-(b) WHERE r.person="Bruce" RETURN a.name as device, r.person as person, r.opinion as opinion, b.name as feature; MATCH (a)-[r]-(b) WHERE r.person="Kayla" RETURN a.name as device, r.person as person, r.opinion as opinion, b.name as feature
Question: {question}
Query: """,
    "similar_manf_opinions": """Generate Cypher query (or several queries, if necessary) from the question by analogy with examples given.
Question example: Whose opinions from Linda and Arianna about manufacturers are most similar to Hugh's?
Query example: MATCH (m)<-[r2:manufacturer]-(a)-[r1]-(b) WHERE r1.person="Linda" RETURN a.name as device, r1.person as person, r1.opinion as opinion, b.name as feature, m.name as manufacturer; MATCH (m)<-[r2:manufacturer]-(a)-[r1]-(b) WHERE r1.person="Arianna" RETURN a.name as device, r1.person as person, r1.opinion as opinion, b.name as feature, m.name as manufacturer; MATCH (m)<-[r2:manufacturer]-(a)-[r1]-(b) WHERE r1.person="Hugh" RETURN a.name as device, r1.person as person, r1.opinion as opinion, b.name as feature, m.name as manufacturer;
Question: {question}
Query: """,
    "which_people_about_device": """Generate Cypher query from the question by analogy with examples given.
Question example: Which people have neg opinion about front camera of iPhone ProMax?
Query example: MATCH (a)-[r]-(b) WHERE a.name="iPhone_ProMax" AND b.name="front_camera" AND r.sentiment="neg" RETURN a.name AS device, r.person AS person, r.sentiment AS sentiment, b.name AS feature
Question: {question}
Query: """,
    "dominant_opinion": """Generate Cypher query from the question by analogy with examples given.
Question example: What Freda's opinion (positive, negative or neutral) about front camera of One Plus was dominant during using One Plus?
Query example: MATCH (a)-[r]-(b) WHERE a.name="One_Plus" AND b.name="front_camera" AND r.person="Freda" RETURN a.name AS device, r.person AS person, r.opinion AS opinion, b.name AS feature
Question: {question}
Query: """,
    "last_opinion": """Generate Cypher query from the question by analogy with examples given.
Question example: What opinion (positive, negative or neutral) about module design of One Plus was last during Emma's experience of One Plus?
Query example: MATCH (a)-[r]-(b) WHERE a.name="One_Plus" AND b.name="module_design" AND r.person="Emma" RETURN a.name AS device, r.person AS person, r.opinion AS opinion, b.name AS feature
Question: {question}
Query: """
}

with open("question_in_context_examples.json", 'r') as inp:
    in_context_examples = json.load(inp)

prompt_answer_template = """Answer the question, based on provided info by analogy with examples given. Avoid giving None final answer, if you are not sure, give a guess answer. None answers are strictly prohibited. Generate chain of thought and then give the final answer in the following format:
### Answer
Chain of thought: ... Final answer: ...
{examples}
Question {n}: {question}
Info {n}: {info}
### Answer {n} """

in_context_questions = [element["question"] for element in in_context_examples]
in_cont_embs = retriever.embed(in_context_questions)

log_flname = "gigachat_log2.txt"
num_in_cont = 3

for flname in [
    # "compare_questions.json",
    # "compare_sentiment.json",
    # "device_sentiment.json",
    # "same_devices.json",
    # "same_manufacturer.json",
    "similar_device_opinions.json",
    # "similar_manf_opinions.json",
    "which_people_about_device.json",
    "dominant_opinion.json",
    "last_opinion.json"
]:
    with open(f"questions/{flname}", 'r') as inp:
        questions = json.load(inp)
    qas = []
    answers_flname = f"answers_gigachat/{flname.replace('.json', '')}_gigachat.json"
    if os.path.exists(answers_flname):
        with open(answers_flname, 'r') as inp:
            qas = json.load(inp)
    start_n = len(qas)

    for n, question_info in enumerate(questions[20:25]):
        question = question_info["question"]

        query = [question]
        query_embs = retriever.embed(query)
        result = retriever.search_in_embeds(in_cont_embs, query_embs, 5)
        idx = result["idx"][0][:num_in_cont]
        retr_questions = [in_context_questions[ind] for ind in idx]
        retr_in_cont_examples = [in_context_examples[ind] for ind in idx]

        gold_answer = question_info["answer"]
        with open(log_flname, 'a') as out:
            out.write(f"{n} --- {question}"+'\n')
            out.write(f"gold_answer: {gold_answer}"+'\n')
        prompt = prompt_query_templates[flname.replace(
            ".json", "")].format(question=question)
        try:
            res = giga.chat(prompt)
            queries_info = res.choices[0].message.content
            with open(log_flname, 'a') as out:
                out.write(f"queries_info: {queries_info}"+'\n')
            if ";" in queries_info:
                queries = queries_info.split(";")
                queries = [query.strip() for query in queries]
            else:
                queries = [queries_info.strip()]
            print("queries", queries)
            with open(log_flname, 'a') as out:
                out.write(f"queries: {queries}"+'\n')
            info = []
            for query in queries:
                entities = re.findall(r"\.([A-Za-z0-9]+)=\"(.*?)\"", query)
                for label, entity_name in entities:
                    if label != "person":
                        f_entity_name = entity_name.lower().replace(" ", "_")
                        query = query.replace(entity_name, f_entity_name)
                entities = re.findall(r'(".*?")', query)
                for entity in entities:
                    entity_clean = entity.strip('"').replace("_", " ")
                    if entity_clean not in question and entity_clean.replace(" ", "") in question:
                        query = query.replace(entity.strip(
                            '"'), entity_clean.replace(" ", ""))
                res = conn.execute_query(query, db="testdb")
                print(f"query: {query} --- res: {res}")
                with open(log_flname, 'a') as out:
                    out.write(f"query: {query} --- result: {res}"+'\n')

                for element in res:
                    info_element = element.data()
                    info_element = [f"{key.replace('_', ' ')}: {value.replace('_', ' ')}"
                                    for key, value in info_element.items()]
                    info_element_str = ", ".join(info_element)
                    if info_element_str not in info:
                        info.append(info_element_str)
            info_str = "; ".join(info)
        except Exception as e:
            print(f"error: {e}")
            info_str = ""

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

        prompt = prompt_answer_template.format(
            examples=in_cont_examples_str, n=num_in_cont+1, question=question, info=info_str)
        with open(log_flname, 'a') as out:
            out.write('\n')
            out.write(f"prompt_answer: {prompt}"+'\n')

        res = giga.chat(prompt)
        res_init = res.choices[0].message.content
        res = copy.deepcopy(res_init)
        pred_answer = ""
        found_line = ""
        for line in res.split("\n"):
            if f"Final answer {num_in_cont}" in line:
                found_line = line
                break
        if not found_line and f"Final answer {num_in_cont + 1}" in res:
            fnd = res.find(f"Final answer {num_in_cont + 1}")
            found_line = res[fnd:]

        if found_line:
            pred_answer = found_line.split(
                f"Final answer {num_in_cont + 1}: ")[-1]
        elif len(res.split("\n")) > 1:
            pred_answer = res.split("\n")[1]
        else:
            pred_answer = ""
        pred_answer = pred_answer.split(f"Question {num_in_cont + 2}")[0]
        with open(log_flname, 'a') as out:
            out.write(f"res_init: {res_init}"+'\n')
            out.write(f"pred_answer: {pred_answer}"+'\n')
            out.write("_"*60+'\n\n')

        qas.append({"n": n,
                    "question": question,
                    "info": info_str,
                    "gold_answer": gold_answer,
                    "pred_answer": pred_answer
                    })
        with open(f"answers_gigachat/{flname.replace('.json', '')}_gigachat_test.json", 'w') as out:
            json.dump(qas, out, indent=2)
        print("gold_answer", gold_answer)
        print("pred_answer", pred_answer)
        print("_"*60)

print("finished")
