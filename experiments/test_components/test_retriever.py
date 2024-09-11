import json
from retrieve.retriever import Retriever

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
idx = result["idx"][0]
print([entities_dict["feature"][ind] for ind in idx])