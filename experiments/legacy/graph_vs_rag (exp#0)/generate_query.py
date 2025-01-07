import os
import transformers
import torch

os.environ['HF_HOME'] = '/archive/evseev.cache'

model_name = "Undi95/Meta-Llama-3-8B-Instruct-hf"

pipeline = transformers.pipeline(
    "text-generation",
    model=model_name,
    model_kwargs={"torch_dtype": torch.bfloat16},
    device_map="auto",
    max_new_tokens=200
)

prompt = """Generate Cypher query from the question by analogy with examples given.
Question example: Lily has positive, negative or neutral opinion about photography camera of XiaoMi 10pro?
Query example: MATCH (a)-[r]-(b) WHERE a.name="XiaoMi_10pro" AND b.name="photography_camera" AND r.person="Lily" RETURN a.name as device, r.person as person, type(r) as opinion, b.name as feature
Question: Leonars has positive, negative or neutral opinion about Front camera of Huawei?
Query: """

res = pipeline(prompt)
queries_info = res[0]["generated_text"].split(prompt)[-1].split("\n")[0].strip()
print(queries_info)
