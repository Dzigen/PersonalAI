import json
import os
from openai import OpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings

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


with open("utterances_for_test.json", 'r') as inp:
    utterances = json.load(inp)

if os.path.exists("./diaasq_db"):
    print("index already exists")
    vectordb = Chroma(
        persist_directory="./diaasq_db",
        embedding_function=OpenAIEmbeddings()
    )
else:
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=50)
    documents = text_splitter.create_documents(utterances)
    print(len(documents))
    print(documents[0])
    vectordb = Chroma.from_documents(
        documents,
        embedding=OpenAIEmbeddings(),
        persist_directory="./diaasq_db",
    )
print("built vectordb")

vectordb.persist()
retriever = vectordb.as_retriever(search_kwargs={"k": 10})

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

PROMPT_ANSWER = """Generate answer to the question using information, extracted from the database.
Question: {question}
Information from the database: {info}
Answer: """

qas = []
for question_type in ["simple_sentiment", "compare_devices", "compare_sentiment"]:
    for question in questions_dict[question_type]:
        res = retriever.get_relevant_documents(query=question)
        retr_elements = []
        for element in res:
            if element.page_content not in retr_elements:
                retr_elements.append(element.page_content)
        prompt = PROMPT_ANSWER.format(question=question, info="\n".join(retr_elements))
        res = execute_prompt(prompt)
        qas.append([question, res])

with open("qas_rag.json", 'w') as out:
    json.dump(qas, out, indent=2)