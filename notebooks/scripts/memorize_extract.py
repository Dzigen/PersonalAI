import sys
import json
from tqdm import tqdm
import joblib
import gc

# TO CHANGE
BASEDIR = "/workspace"
# TO CHNAGE

sys.path.insert(0, BASEDIR)
from src.utils.data_structs import RelationType, NodeType
from src.memorize_pipeline.extractor.LLMExtractor import LLMExtractor
from src.agents.private import GigaChatAgent

DATASET_PATH = '../../data/Augment_DiaASQ.json'
SAVE_EXTRACTED_TRIPLETS_FILE = "tmp_extracted_gigachat_triplets.dump"
gc.collect()

###########

print("loading dataset...")

with open(DATASET_PATH, 'r', encoding='utf-8') as fd:
    data = json.loads(fd.read())

raw_texts = list(map(lambda v: v['text_dialog'], data['data']))
raw_time = list(map(lambda v: v['time'].split(',')[0].strip(), data['data']))
print(len(raw_texts), len(raw_time))

print("initing agent and llm-extractor...")

agent = GigaChatAgent()
extractor = LLMExtractor(agent_conn=agent)

###########

print("start extracting triplets...")

extracted_triplets = []
for i in tqdm(range(len(raw_texts))):
    out = extractor.extract(raw_texts[i])
    extracted_triplets.append(out)

###########

print("adding time to triplets...")

for group_idx in tqdm(range(len(extracted_triplets))):
    cur_time = raw_time[group_idx]
    for triplet_idx in range(len(extracted_triplets[group_idx])):
        if extracted_triplets[group_idx][triplet_idx].relation.type == RelationType.simple:
            extracted_triplets[group_idx][triplet_idx].relation.prop['time'] = cur_time
        else:
            extracted_triplets[group_idx][triplet_idx].end_node.prop['time'] = cur_time
            if extracted_triplets[group_idx][triplet_idx].start_node.type != NodeType.object:
                extracted_triplets[group_idx][triplet_idx].start_node.prop['time'] = cur_time

print("saving triplets...")

print(sum(list(map(len, extracted_triplets))))
joblib.dump(extracted_triplets, SAVE_EXTRACTED_TRIPLETS_FILE)

print("DONE")