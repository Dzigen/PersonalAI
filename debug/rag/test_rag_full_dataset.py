import os
import json
import torch
import numpy as np
from tqdm.auto import tqdm

from src.utils.utils2 import Logger
from src.utils.contriever import Retriever
from agents.llama_agent import LLaMAagent, LLaMAagentLocal


def test(n_u, n_d, utt_emb, dialogs_emb, dataset, utterances, dialogs, add_manf_info, agent, log):
    results = []
    for task in tqdm(dataset, "iterations over questions"):
        retrieved = ""
        if n_u > 0:
            retrieved += "\nRelevant utterances:\n"
            best_ids = (utt_emb @ task["embedding"]
                        ).topk(n_u).indices.cpu().detach().numpy()
            retrieved += "\n".join(utterances[best_ids])
        if n_d > 0:
            retrieved += "\n\nRelevant dialogs:\n\n"
            best_ids = (dialogs_emb @ task["embedding"]
                        ).topk(n_d).indices.cpu().detach().numpy()
            retrieved += "\n\n".join(dialogs[best_ids])

        question = task["question"]
        log("QUESTION: " + str(question))
        log("RETRIEVED: " + str(retrieved))
        log("RIGHT ANSWER: " + str(task["answer"]))
        if add_manf_info:
            retrieved += """\nAvailable manufacturer: Xiaomi, Apple, OnePlus, Vivo, Honor, Huawei, Samsung
Redmi and Note is made by Xiaomi, Iphone is made by Apple\n\n"""
        prompt = f'''Your task is answer the question: {question}

You are provided with relevant memories about dialogs: {retrieved}

Question: {question} This is a closed question, the answer choices are listed in its text.
You must respond with one of these options and nothing else.
Answer: '''
        answer = agent.generate(prompt).lower()
        log("MODEL ANSWER: " + str(answer))
        results.append(task["answer"].strip('''"' .,:-''').lower() in answer)
        log("CURRENT ACCURACY: " + str(np.mean(results)))
        log("==" * 30 + "\n")


n_utt, n_dia, n_utt_mix, n_dia_mix = [5, 10, 15, 20, 25], [
    3, 5, 7, 10, 15], [5, 7, 10, 12, 15], [2, 3, 5, 7, 10]
log_path = "test_rag/full_1"
batch_size = 16

embedder = Retriever("cpu")
log = Logger(log_path)
agent = LLaMAagent("You are a helpful assistant")

with open("testDiaASQ/Augment_DiaASQ.json") as f:
    data = json.load(f)
utterances, dialogs = set(), set()
for dialog in data["data"]:
    dia_utterances = dialog["text_dialog"].split('\n')
    utterances |= set(dia_utterances)
    dialogs.add(dialog["text_dialog"])

utterances, dialogs = list(utterances), list(dialogs)
utt_emb = []
for i in tqdm(range(len(utterances) // batch_size), "batches of utterances"):
    utt_emb.append(embedder.embed(
        utterances[i * batch_size: (i + 1) * batch_size]))
utt_emb = torch.cat(utt_emb, axis=0)

dialogs_emb = []
for i in tqdm(range(len(dialogs) // batch_size), "batches of dialogs"):
    dialogs_emb.append(embedder.embed(
        dialogs[i * batch_size: (i + 1) * batch_size]))
dialogs_emb = torch.cat(dialogs_emb, axis=0)

utterances, dialogs = np.array(utterances), np.array(dialogs)

log(f"Utterances shape: {str(utt_emb.shape)}, Dialogs shape: {str(dialogs_emb.shape)}")

questions = os.listdir("testDiaASQ/questions")
dataset = {}
for filename in questions:
    with open("testDiaASQ/questions/" + filename) as f:
        quest = json.load(f)

    for task in quest:
        task["embedding"] = embedder.embed([task["question"]])[0]
    dataset[filename.split(".")[0]] = quest


for_manufactured_info = ["same_manufacturer", "similar_manf_opinions"]
names = list(dataset.keys())

for n_u in n_utt:
    for question_type in names:
        log.__init__(log_path + f"/utt_only_{n_u}_{question_type}")
        add_manf_info = question_type in for_manufactured_info
        test(n_u, 0, utt_emb, dialogs_emb,
             dataset[question_type], utterances, dialogs, add_manf_info, agent, log)

for n_d in n_dia:
    for question_type in names:
        log.__init__(log_path + f"/dia_only_{n_d}_{question_type}")
        add_manf_info = question_type in for_manufactured_info
        test(0, n_d, utt_emb, dialogs_emb,
             dataset[question_type], utterances, dialogs, add_manf_info, agent, log)

for n_u, n_d in zip(n_utt_mix, n_dia_mix):
    for question_type in names:
        log.__init__(log_path + f"/mix_{n_u}_{n_d}_{question_type}")
        add_manf_info = question_type in for_manufactured_info
        test(n_u, n_d, utt_emb, dialogs_emb,
             dataset[question_type], utterances, dialogs, add_manf_info, agent, log)
