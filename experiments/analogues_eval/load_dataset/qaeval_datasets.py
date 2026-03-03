from typing import List, Tuple, Dict
import json
import pandas as pd
import os

def diaasqa_qa_load(dataset_path: str, max_samples_per_pack: int = -1) -> List[Tuple[str, List[str], List[str]]]:
    eval_dir_path = f"{dataset_path}/qa_eval"
    pack_files = os.listdir(eval_dir_path)
    packs = []

    for pack_f in pack_files:
        with open(f"{eval_dir_path}/{pack_f}", 'r', encoding='utf-8') as fd:
            data = json.loads(fd.read())

        pack_name = '.'.join(pack_f.split('.')[:-1])
        questions = list(map(lambda item: item['question'], data))
        answers = list(map(lambda item: item['answer'], data))

        max_samples = max_samples_per_pack
        if (max_samples > 0):
            questions = questions[:max_samples]
            answers = answers[:max_samples]

        packs.append((pack_name, questions, answers))

    return packs

def hotpotqa_distractor_validation_qa_load(dataset_path: str, max_samples_per_pack: int = -1) -> List[Tuple[str, List[str], List[str]]]:
    qa_df = pd.read_csv(f"{dataset_path}/qa_pairs.csv")

    questions = qa_df['question'].tolist()
    answers = qa_df['answer'].tolist()

    max_samples = max_samples_per_pack
    if (max_samples > 0):
        questions = questions[:max_samples]
        answers = answers[:max_samples]

    packs = [['all', questions, answers]]

    return packs

def trivia_qa_rcwikipedia_validation_qa_load(dataset_path: str, max_samples_per_pack: int = -1) -> List[Tuple[str, List[str], List[str]]]:
    qa_df = pd.read_csv(f"{dataset_path}/qa_pairs.csv")

    questions = qa_df['question'].tolist()
    answers = qa_df['answer'].tolist()

    max_samples = max_samples_per_pack
    if (max_samples > 0):
        questions = questions[:max_samples]
        answers = answers[:max_samples]

    packs = [['all', questions, answers]]

    return packs

def rubqdev_qa_load(dataset_path: str, max_samples_per_pack: int = -1) -> List[Tuple[str, Dict[str, str]]]:
    qa_df = pd.read_csv(f"{dataset_path}/qa_pairs.csv")

    questions = qa_df['question'].tolist()
    answers = qa_df['answer'].tolist()

    max_samples = max_samples_per_pack
    if (max_samples > 0):
        questions = questions[:max_samples]
        answers = answers[:max_samples]

    packs = [['all', questions, answers]]

    return packs

def sberdialogues_qa_load(dataset_path: str, max_samples_per_pack: int = -1) -> List[Tuple[str, List[str], List[str]]]:
    eval_dir_path = f"{dataset_path}/qa_eval"
    pack_files = os.listdir(eval_dir_path)
    packs = []

    for pack_f in pack_files:
        with open(f"{eval_dir_path}/{pack_f}", 'r', encoding='utf-8') as fd:
            data = json.loads(fd.read())

        pack_name = '.'.join(pack_f.split('.')[:-1])
        questions = list(map(lambda item: item['question'], data))
        answers = list(map(lambda item: item['answer'], data))

        max_samples = max_samples_per_pack
        if (max_samples > 0):
            questions = questions[:max_samples]
            answers = answers[:max_samples]

        packs.append((pack_name, questions, answers))

    return packs

def musique_validation_qa_load(dataset_path: str, max_samples_per_pack: int = -1) -> List[Tuple[str, Dict[str, str]]]:
    qa_df = pd.read_csv(f"{dataset_path}/qa_pairs.csv")

    questions = qa_df['question'].tolist()
    answers = qa_df['answer'].tolist()

    max_samples = max_samples_per_pack
    if (max_samples > 0):
        questions = questions[:max_samples]
        answers = answers[:max_samples]

    packs = [['all', questions, answers]]

    return packs

def wiki2multihopqa_dev_qa_load(dataset_path: str, max_samples_per_pack: int = -1) -> List[Tuple[str, Dict[str, str]]]:
    qa_df = pd.read_csv(f"{dataset_path}/qa_pairs.csv")

    questions = qa_df['question'].tolist()
    answers = qa_df['answer'].tolist()

    max_samples = max_samples_per_pack
    if (max_samples > 0):
        questions = questions[:max_samples]
        answers = answers[:max_samples]

    packs = [['all', questions, answers]]

    return packs

def natural_questions_train_qa_load(dataset_path: str, max_samples_per_pack: int = -1) -> List[Tuple[str, Dict[str, str]]]:
    qa_df = pd.read_csv(f"{dataset_path}/qa_pairs.csv")

    questions = qa_df['question'].tolist()
    answers = qa_df['answer'].tolist()

    max_samples = max_samples_per_pack
    if (max_samples > 0):
        questions = questions[:max_samples]
        answers = answers[:max_samples]

    packs = [['all', questions, answers]]

    return packs

CUSTOM_LOAD_QAEVAL_FUNCS = {
    'diaasq': diaasqa_qa_load,
    'rubq_dev': rubqdev_qa_load,
    'hotpotqa_distractor_validation': hotpotqa_distractor_validation_qa_load,
    'trivia_qa_rcwikipedia_validation': trivia_qa_rcwikipedia_validation_qa_load,
    'musique_validation': musique_validation_qa_load,
    '2wikimultihopqa_dev': wiki2multihopqa_dev_qa_load,
    'natural_questions_train': natural_questions_train_qa_load
}
CUSTOM_LOAD_QAEVAL_FUNCS.update({f'sberdialogues_conv-{i}': sberdialogues_qa_load for i in range(1,36)})
