from typing import List, Tuple, Dict
import json
import pandas as pd
from datasets import load_from_disk
import os


def diaasq_cload(dataset_path: str) -> List[Tuple[str, Dict[str, str]]]:
    with open(f"{dataset_path}/Augment_DiaASQ.json", 'r', encoding='utf-8') as fd:
        data = json.loads(fd.read())

    data_pairs = []
    for item in data['data']:
        data_pairs.append(
            (item['text_dialog'], item['time'].split(',')[0], dict()))

    return data_pairs


def hotpotqa_distractor_validation_cload(dataset_path: str) -> List[Tuple[str, Dict[str, str]]]:
    contexts_df = pd.read_csv(f"{dataset_path}/relevant_contexts.csv")

    data_pair = []
    for r_idx in range(contexts_df.shape[0]):
        formated_context = f"Title: {contexts_df['title'][r_idx]}\n{contexts_df['context'][r_idx]}"
        data_pair.append((formated_context, None, dict()))
    print(len(data_pair), contexts_df.shape)
    return data_pair


def triviaqa_rcwikipedia_validation_cload(dataset_path: str) -> List[Tuple[str, Dict[str, str]]]:
    contexts_df = pd.read_csv(f"{dataset_path}/relevant_contexts.csv")

    data_pair = []
    for r_idx in range(contexts_df.shape[0]):
        formated_context = f"Title: {contexts_df['title'][r_idx]}\n{contexts_df['context'][r_idx]}"
        data_pair.append((formated_context, None, dict()))

    return data_pair

def rubqdev_cload(dataset_path: str) -> List[Tuple[str, Dict[str, str]]]:
    contexts_df = pd.read_csv(f"{dataset_path}/relevant_contexts.csv")

    data_pair = []
    for r_idx in range(contexts_df.shape[0]):
        formated_context = contexts_df['context'][r_idx]
        data_pair.append((formated_context, None, dict()))

    return data_pair

def sberdialogues_cload(dataset_path: str) -> List[Tuple[str, Dict[str, str]]]:
    contexts_df = pd.read_csv(f"{dataset_path}/relevant_contexts.csv")

    data_pair = []
    for r_idx in range(contexts_df.shape[0]):
        formated_context = contexts_df['context'][r_idx]
        raw_properties = ast.literal_eval(contexts_df['properties'][r_idx])
        session_time = list(filter(lambda p: p[0].endswith("date_time"), raw_properties.items()))[0][1]
        data_pair.append((formated_context, session_time, dict()))

    return data_pair

def musique_validation_cload(dataset_path: str) -> List[Tuple[str, Dict[str, str]]]:
    contexts_df = pd.read_csv(f"{dataset_path}/relevant_contexts.csv")

    data_pair = []
    for r_idx in range(contexts_df.shape[0]):
        formated_context = f"Title: {contexts_df['title'][r_idx]}\n{contexts_df['context'][r_idx]}"
        data_pair.append((formated_context, None, dict()))
    print(len(data_pair), contexts_df.shape)
    return data_pair

def wiki2multihopqa_dev_cload(dataset_path: str) -> List[Tuple[str, Dict[str, str]]]:
    contexts_df = pd.read_csv(f"{dataset_path}/relevant_contexts.csv")

    data_pair = []
    for r_idx in range(contexts_df.shape[0]):
        formated_context = f"Title: {contexts_df['title'][r_idx]}\n{contexts_df['context'][r_idx]}"
        data_pair.append((formated_context, None, dict()))
    print(len(data_pair), contexts_df.shape)
    return data_pair

def natural_questions_train_cload(dataset_path: str) -> List[Tuple[str, Dict[str, str]]]:
    contexts_df = pd.read_csv(f"{dataset_path}/relevant_contexts.csv")

    data_pair = []
    for r_idx in range(contexts_df.shape[0]):
        formated_context = contexts_df['context'][r_idx]
        data_pair.append((formated_context, None, dict()))

    return data_pair

def mine_train_kgeval_cload(dataset_path: str) -> List[Tuple[str, List[str], List[str]]]:
    original_dataset = load_from_disk(f"{dataset_path}/original") # 101
    data_pair = []
    for r_idx in range(len(original_dataset)):
        formated_context = original_dataset['essay_content'][r_idx]
        if len(formated_context) < 1:
            continue
        else:
            data_pair.append((formated_context, None, dict()))

    return data_pair

CUSTOM_LOAD_KGBUILD_DS_FUNCS = {
    'diaasq': diaasq_cload,
    'rubq_dev': rubqdev_cload,
    'hotpotqa_distractor_validation': hotpotqa_distractor_validation_cload,
    'trivia_qa_rcwikipedia_validation': triviaqa_rcwikipedia_validation_cload,
    'musique_validation': musique_validation_cload,
    '2wikimultihopqa_dev': wiki2multihopqa_dev_cload,
    'natural_questions_train': natural_questions_train_cload,
    'mine_train_kgeval': mine_train_kgeval_cload
}
CUSTOM_LOAD_KGBUILD_DS_FUNCS.update({f'sberdialogues_conv-{i}': sberdialogues_cload for i in range(1,36)})
