from tqdm import tqdm
import matplotlib.pyplot as plt
import numpy as np
from typing import List, Dict, Tuple, Union, Set
import hashlib
import pandas as pd

def get_hash(text: str) -> str:
    return hashlib.md5((text).encode()).hexdigest()

def get_document_hash(document: Tuple[Union[None,str], str]) -> str:
    title, text = document
    formated_document = f"title: {title}\n{text}"
    return get_hash(formated_document)

def filter_documents_by_len(documents: List[Tuple[Union[None, str], str]], doc_min_len: int, doc_max_len: int) -> List[Tuple[Union[None,str], str]]:
    accepted_documents = []
    for document in documents:
        title, text = document
        formated_document = f"{title}{text}" if title is not None else text
        if (len(formated_document) >= doc_min_len) and (len(formated_document) <= doc_max_len):
            accepted_documents.append(document)
    return accepted_documents

def preprocess_documents(dataset: object, doc_min_len: int, doc_max_len: int, custom_funcs: Dict[str, object]) -> pd.DataFrame:
    unique_document_hashes = set()
    accepted_documents = list()
    for idx in tqdm(range(custom_funcs['get_dataset_len'](dataset))):
        cur_documents = custom_funcs['get_question_documents'](dataset, idx)
        tmp_documents = filter_documents_by_len(cur_documents, doc_min_len, doc_max_len)

        for document in tmp_documents:
            document_hash = get_document_hash(document)
            if document_hash not in unique_document_hashes:
                unique_document_hashes.add(document_hash)
                title, text = document
                accepted_documents.append([title, text, document_hash, idx])

    documents_df = pd.DataFrame(accepted_documents, columns=['title', 'context', 'hash', 'original_qaidx'])
    return documents_df

def is_qapair_accepted_by_reldocs(relevant_documents: List[Tuple[Union[None,str], str]], accepted_document_hashes: Set[str]) -> bool:
    accepted_docs_count = 0
    for document in relevant_documents:
        document_hash = get_document_hash(document)
        if document_hash in accepted_document_hashes:
            accepted_docs_count += 1
    return accepted_docs_count == len(relevant_documents)

def preprocess_qapairs(dataset: object, accepted_documents: pd.DataFrame, max_qapairs: int,
                       custom_funcs: Dict[str, object], sample_strategy: str = 'naive') -> Tuple[pd.DataFrame, pd.DataFrame]:
    unique_qapairs_hashes: Set[str] = set()
    accepted_qapairs = list()

    accepted_relevant_documents = list()
    document_hash_to_idx_map: Dict[str, int] = dict()

    accepted_document_hashes: Set[str] = set(accepted_documents['hash'].tolist())

    qa_max_idx = -1
    cntx_max_idx = -1
    for original_idx in tqdm(range(custom_funcs['get_dataset_len'](dataset))):
        if len(accepted_qapairs) >= max_qapairs:
            break

        question, question_type, answer, relevant_documents = custom_funcs['get_qa_info'](dataset, original_idx)

        question_hash = get_hash(question)
        if question_hash not in unique_qapairs_hashes:
            unique_qapairs_hashes.add(question_hash)
        else:
            continue

        if is_qapair_accepted_by_reldocs(relevant_documents, accepted_document_hashes):

            relevant_document_ids = []
            for document in relevant_documents:
                title, text = document
                document_hash = get_document_hash(document)
                document_idx = document_hash_to_idx_map.get(document_hash, None)

                if document_idx is None:
                    new_cntx_idx = cntx_max_idx + 1
                    document_idx = new_cntx_idx

                    accepted_relevant_documents.append((title, text, document_idx, document_hash))
                    document_hash_to_idx_map[document_hash] = document_idx
                    cntx_max_idx += 1

                relevant_document_ids.append(document_idx)

            new_qaidx = qa_max_idx + 1
            formated_qapair = (question, question_type, answer, relevant_document_ids, new_qaidx, original_idx)
            accepted_qapairs.append(formated_qapair)
            qa_max_idx += 1

    qapairs_df = pd.DataFrame(accepted_qapairs, columns=['question', 'type', 'answer', 'cntx_ids', 'qa_idx', 'original_qaidx'])
    relevant_documents_df = pd.DataFrame(accepted_relevant_documents, columns=['title', 'context', 'cntx_idx', 'hash'])

    return qapairs_df, relevant_documents_df

def select_noise_documents(
        relevant_documents_df: pd.DataFrame, accepted_documents_df: pd.DataFrame,
        noise_documents_amount: int, doc_idx_offset: int = 0, sample_strategy: str = 'naive') -> pd.DataFrame:

    rel_doc_hashes = set(relevant_documents_df['hash'].tolist())
    acc_doc_hashes = set(accepted_documents_df['hash'].tolist())

    tmp_doc_hashes = list(acc_doc_hashes.difference(rel_doc_hashes))
    noise_doc_hashes = tmp_doc_hashes[:noise_documents_amount]

    noise_documents = []
    for doc_idx, doc_hash in tqdm(enumerate(noise_doc_hashes)):
        raw_noise_document = accepted_documents_df.loc[accepted_documents_df['hash'] == doc_hash].reset_index(drop=True)
        formated_noise_document = (raw_noise_document['title'][0], raw_noise_document['context'][0], doc_idx_offset+doc_idx, doc_hash)
        noise_documents.append(formated_noise_document)

    noise_documents_df = pd.DataFrame(noise_documents, columns=['title', 'context', 'cntx_idx', 'hash'])
    return noise_documents_df

def plot_textlen_distribution(dataset: object, column_name):
    cntx_lens = list(map(lambda cntx: len(cntx), dataset[column_name]))
    plt.hist(cntx_lens, bins=50, density=True)
    plt.title(f"'{column_name}' len distribution")
    plt.grid()
    plt.show()

def compute_stats(numbers: List[int]) -> Dict[str, float]:
    return {'median': round(float(np.median(numbers)),5),
            'mean': round(float(np.mean(numbers)),5),
            'std': round(float(np.std(numbers)),5),
            'min': round(min(numbers),5),
            'max': round(max(numbers),5)}

def calculate_dataset_stats(qapairs_df: pd.DataFrame, relevant_documents_df: pd.DataFrame) -> Dict:
    statistics = {
        'contexts_amount': relevant_documents_df.shape[0],
        'contexts_len': compute_stats(list(map(lambda v: len(v), relevant_documents_df['context'].tolist()))),
        'qa_pairs_amount': qapairs_df.shape[0],
        'answers_len':  compute_stats(list(map(lambda v: len(v), qapairs_df['answer'].tolist()))),
        'questions_len': compute_stats(list(map(lambda v: len(v), qapairs_df['question'].tolist()))),
        'rel_contexts_per_question': compute_stats(list(map(lambda v: len(v), qapairs_df['cntx_ids'].tolist())))
    }
    return statistics

def check_dataset_consistency(
        original_dataset: object, qapairs_df: pd.DataFrame,
        relevant_documents_df: pd.DataFrame, custom_funcs: Dict[str, object]) -> bool:
    # qa-pairs: 'question', 'answer', 'cntx_ids', 'qa_idx', 'original_qaidx'
    # relevant_documents: 'title', 'context', 'cntx_idx', 'hash'

    # нет дубликатов контекстов
    unique_documents_amount = len(set(relevant_documents_df['context'].tolist()))
    assert unique_documents_amount == relevant_documents_df.shape[0]

    # нет дубликатов вопросов
    unique_questions_amount = len(set(qapairs_df['question'].tolist()))
    assert unique_questions_amount == qapairs_df.shape[0]

    for idx in tqdm(range(qapairs_df.shape[0])):
        original_qaidx = qapairs_df['original_qaidx'][idx]

        # У qa-пар ненулевое количество сопоставленных релевантных контекстов
        assert type(qapairs_df['cntx_ids'][idx]) is list
        assert len(qapairs_df['cntx_ids'][idx]) > 0

        expected_question, question_type, expected_answer, expected_relevant_documents = custom_funcs['get_qa_info'](original_dataset, original_qaidx)
        # идентификаторы qa-пар соответствуют реальным qa-парам
        assert expected_question == qapairs_df['question'][idx]
        assert expected_answer == qapairs_df['answer'][idx]

        # идентификаторы контекстов в qa парах соответствуют реальным контекстам
        real_relevant_documents: List[Tuple[Union[None,str], str]] = []
        for cntx_idx in qapairs_df['cntx_ids'][idx]:
            raw_relevant_document = relevant_documents_df[relevant_documents_df['cntx_idx'] == cntx_idx].reset_index(drop=True)
            title, text = raw_relevant_document['title'][0], raw_relevant_document['context'][0]
            real_relevant_documents.append((title, text))
        assert set(expected_relevant_documents) == set(real_relevant_documents)

    return True
