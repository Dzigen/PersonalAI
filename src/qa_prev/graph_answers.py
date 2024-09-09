import json
from openai import OpenAI
from neo4j_functions import Neo4jConnection

conn = Neo4jConnection(uri="bolt://31.207.47.254:7687", user="neo4j", pwd="password")

OPENAI_API_KEY=""

model = "gpt-4o"
client = OpenAI(api_key=OPENAI_API_KEY)

def execute_prompt(prompt):
    if isinstance(prompt, str):
        content = [{"role": "system", "content": prompt}]
    else:
        content = prompt
    response = client.chat.completions.create(model=model, messages=content)
    response = response.choices[0].message.content
    return response

PROMPT_TEMPLATE = """Generate Cypher query (or several queries, if necessary) from the question by analogy with examples given.
Question example 1: Which device is better in battery life: k30u or 13promax?
Query example 1: MATCH (a)-[r]-(b) WHERE a.name="k30u" AND b.name="battery_life" AND r.sentiment="pos" RETURN count(*) AS number_for_k30u; MATCH (a)-[r]-(b) WHERE a.name="13promax" AND b.name="battery_life" AND r.sentiment="pos" RETURN count(*) AS number_for_13promax
Question example 2: The majority of speakers have positive, neutral or negative sentiment about camera of Xiaomi?
Query example 2: MATCH (a)-[r]-(b) WHERE a.name="Xiaomi" AND b.name="camera" RETURN r.sentiment AS sentiment, count(*) AS number
Question example 3: Kayla has positive, negative or neutral opinion about video of 10PRO?
Query example 3: MATCH (a)-[r]-(b) WHERE a.name="10PRO" AND b.name="video" AND r.person="Kayla" RETURN r.sentiment AS opinion
Question example 4: What does Kayla say about 10PRO?
Query example 4: MATCH (a)-[r]-(b) WHERE a.name="10PRO" AND r.person="Kayla" RETURN r AS says, b.name as feature
Question: {question}
Query: """

PROMPT_TEMPLATES = {
    "simple_sentiment": """Generate Cypher query (or several queries, if necessary) from the question by analogy with examples given.
Question example: Kayla has positive, negative or neutral opinion about video of 10 PRO?
Query example: MATCH (a)-[r]-(b) WHERE a.name="10_PRO" AND b.name="video" AND r.person="Kayla" RETURN r.sentiment AS opinion
Question: {question}
Query: """,
    "simple_triplet": """Generate Cypher query (or several queries, if necessary) from the question by analogy with examples given.
Question example: What does Kayla say about 10PRO?
Query example: MATCH (a)-[r]-(b) WHERE a.name="10PRO" AND r.person="Kayla" RETURN r AS says, b.name as feature
Question: {question}
Query: """,
    "compare_devices": """Generate Cypher query (or several queries, if necessary) from the question by analogy with examples given. In the query leave a.name and b.name the same way as in the example (avoid changing a.name and b.name).
Question example: Which device is better in battery life: k30u or 13 promax?
Query example: MATCH (a)-[r]-(b) WHERE a.name="k30u" AND b.name="battery_life" AND r.sentiment="pos" RETURN count(*) AS positive_opinions_for_k30u; MATCH (a)-[r]-(b) WHERE a.name="k30u" AND b.name="battery_life" AND r.sentiment="neg" RETURN count(*) AS negative_opinions_for_k30u; MATCH (a)-[r]-(b) WHERE a.name="13_promax" AND b.name="battery_life" AND r.sentiment="pos" RETURN count(*) AS positive_opinions_for_13promax; MATCH (a)-[r]-(b) WHERE a.name="13_promax" AND b.name="battery_life" AND r.sentiment="neg" RETURN count(*) AS negative_opinions_for_13promax
Question: {question}
Query: """,
    "compare_sentiment": """Generate Cypher query (or several queries, if necessary) from the question by analogy with examples given.
Question example: The majority of speakers have positive, neutral or negative sentiment about camera of Xiaomi Redmi Note?
Query example: MATCH (a)-[r]-(b) WHERE a.name="Xiaomi_Redmi_Note" AND b.name="camera" RETURN r.sentiment AS sentiment, count(*) AS number
Question: {question}
Query: """,
}

questions_dict = {
    "simple_sentiment": 
        ["Kayla has positive, negative or neutral opinion about video of Xiaomi 10Pro?",
         "Emily has positive, negative or neutral opinion about pictures of Mi 11?",
         "Alfred has positive, negative or neutral opinion about heat of Xiaomi 11Pro?",
         "Simon has positive, negative or neutral opinion about charging of Mi 9?",
         "Anthony has positive, negative or neutral opinion about maintenance point of Xiaomi?"],
    "simple_triplet": 
        ["What did Lily say about XiaoMi?",
         "What did Jacob think about photography camera module of MIX4?",
         "What did Alfred say about heat of Xiaomi 11Pro?",
         "What did Kathryn think about Xiaomi 9?",
         "What did Anthony say about maintenance point of Xiaomi?"],
    "compare_devices": 
        ["Which device is better in battery life: 13promax or 13pro?",
         "Which device has better screen: K40 or Xiaomi 11Pro?",
         "Which devices have better screen: Xiaomi or Huawei?",
         "Which devices have more stable signal: Huawei or Apple?",
         "Which device is better in charging: M20 or iQOO9 series?"],
    "compare_sentiment": 
        ["The majority of speakers have positive, neutral or negative sentiment about system of Nubia?",
         "The majority of speakers have positive, neutral or negative sentiment about signal of Huawei?",
         "The majority of speakers have positive, neutral or negative sentiment about back cover design of 11u?",
         "The majority of speakers have positive, neutral or negative sentiment about battery life of 13mini?",
         "The majority of speakers have positive, neutral or negative sentiment about screen of 10s?"],
}

"""
for question_type, questions in questions_dict.items():
    if question_type == "compare_devices":
        prompt = PROMPT_TEMPLATES[question_type].format(question=questions[0])
        res = execute_prompt(prompt)
        print(questions[0])
        print(question_type, res)
        print("_"*60)
"""

queries = [
    """MATCH (a)-[r]-(b) WHERE a.name="XiaoMi" AND b.name="power" AND r.person="Lily" RETURN r.sentiment AS opinion""",
    """MATCH (a)-[r]-(b) WHERE a.name="XiaoMi" AND r.person="Lily" RETURN type(r) AS says, b.name as feature""",
    """MATCH (a)-[r]-(b) WHERE a.name="Apple" AND b.name="battery_life" AND r.sentiment="pos" RETURN count(*) AS number_for_Apple""",
    """MATCH (a)-[r]-(b) WHERE a.name="Huawei" AND b.name="battery_life" AND r.sentiment="pos" RETURN count(*) AS number_for_Huawei""",
    """MATCH (a)-[r]-(b) WHERE a.name="vivo" AND b.name="system" RETURN r.sentiment AS sentiment, count(*) AS number"""
]

"""
for query in queries:
    print("---", query)
    res = conn.execute_query(query, db="testdb")
    for element in res:
        print(element.data())
    print("_"*60)
"""

PROMPT_ANSWER = """Generate answer to the question using information, extracted from the database.
Question: {question}
Information from the database: {info}
Answer: """

qas = []
for question_type in ["simple_sentiment"]:
    for n, question in enumerate(questions_dict[question_type]):
        if n in [1, 3]:
            try:
                prompt = PROMPT_TEMPLATES[question_type].format(question=question)
                res = execute_prompt(prompt)
                if ";" in res:
                    queries = res.split(";")
                    queries = [query.strip() for query in queries]
                else:
                    queries = [res.strip()]
                info = []
                for query in queries:
                    res = conn.execute_query(query, db="testdb")
                    print(f"query: {query} --- res: {res}")
                    with open("graph_answers_log.txt", 'a') as out:
                        out.write(f"question: {question}"+'\n')
                        out.write(f"query: {query} --- res: {res}"+'\n\n')
                    for element in res:
                        info_element = element.data()
                        info_element = [f"{key}: {value}" for key, value in info_element.items()]
                        info += info_element
                info_str = ", ".join(info)
                prompt = PROMPT_ANSWER.format(
                    question=question,
                    info=info_str
                )
                res = execute_prompt(prompt)
                qas.append([question, res])
                print(res)
            except Exception as e:
                print(f"--- in: {question} --- error: {e}")

with open("qas2.json", 'w') as out:
    json.dump(qas, out, indent=2)
print("finished")