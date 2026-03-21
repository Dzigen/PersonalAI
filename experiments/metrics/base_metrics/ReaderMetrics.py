from tqdm import tqdm
from torchmetrics.text.rouge import ROUGEScore
from torchmetrics.text import BLEUScore
import evaluate
import numpy as np
from typing import List
from tqdm import tqdm
from torchmetrics.text.bert import BERTScore
from Levenshtein import distance as levenshtain_distance
import os
import nltk
nltk.download('wordnet')
nltk.download('punkt')

def calculate_f1_generation(hypothesis, reference):
    """
    Calculates F1 score for a single reference and hypothesis pair
    based on word overlap (often used in generation tasks like summarization/translation eval).
    """
    # Tokenize the sentences into words
    reference_tokens = nltk.word_tokenize(reference)
    hypothesis_tokens = nltk.word_tokenize(hypothesis)

    # Calculate precision and recall based on set overlap
    common_tokens = set(reference_tokens) & set(hypothesis_tokens)
    num_common = len(common_tokens)
    num_hyp = len(hypothesis_tokens)
    num_ref = len(reference_tokens)

    # Handle edge cases for division by zero
    precision = num_common / num_hyp if num_hyp > 0 else 0
    recall = num_common / num_ref if num_ref > 0 else 0

    # Calculate F1 score (harmonic mean)
    if precision + recall == 0:
        f1 = 0
    else:
        f1 = 2 * (precision * recall) / (precision + recall)

    return f1

class ReaderMetrics:
    # Source: https://amitness.com/2020/08/information-retrieval-evaluation/

    # Retrieval metrics
    # - mAP
    # - MRR
    # - precision
    # - recall
    # - f1
    # Reader metrics
    # - BLEU presision
    # - ROUGE recall
    # - METEOR f1
    def __init__(self, model_path: str,
                 meteor_filep: str = "./metrics/meteor",
                 em_filep: str = "./metrics/exact_match"):
        self.rouge_obj = ROUGEScore()
        self.bleu1_obj = BLEUScore(n_gram=1)
        self.bleu2_obj = BLEUScore(n_gram=2)
        print("Loading Meteor...")
        self.meteor_obj = evaluate.load(meteor_filep)
        print("Loading ExactMatch")
        self.em_obj = evaluate.load(em_filep)
        print("Loading BertScore")
        self.bertscore_obj = BERTScore(model_path, return_hash=True)

    def bertscore(self, predicted: List[str], targets: List[str]):
        output = self.bertscore_obj(predicted, targets)
        output['precision'] = round(float(output['precision'].mean()), 5)
        output['recall'] = round(float(output['recall'].mean()), 5)
        output['f1'] = round(float(output['f1'].mean()), 5)

        return output

    def rougel(self, predicted: List[str], targets: List[str]):
        return [float(self.rouge_obj(
            predicted[i], targets[i])['rougeL_fmeasure'])
            for i in tqdm(range(len(targets)))]

    def bleu1(self, predicted: List[str], targets: List[str]):
        return [float(self.bleu1_obj(
            [predicted[i]], [[targets[i]]]))
            for i in tqdm(range(len(targets)))]

    def bleu2(self, predicted: List[str], targets: List[str]):
        return [float(self.bleu2_obj(
            [predicted[i]], [[targets[i]]]))
            for i in tqdm(range(len(targets)))]

    def meteor(self, predicted: List[str], targets: List[str]):
        return [float(self.meteor_obj.compute(
            predictions=[predicted[i]], references=[targets[i]])['meteor'])
            for i in tqdm(range(len(targets)))]

    def exact_match(self, predicted: List[str], targets: List[str]):
        return [float(self.em_obj.compute(
            predictions=[predicted[i]], references=[targets[i]], ignore_case=True, ignore_punctuation=True)["exact_match"])
            for i in tqdm(range(len(targets)))]

    def levenshtain_score(self, predicted: List[str], targets: List[str]):
        return list(map(lambda pair: levenshtain_distance(pair[1], pair[0]), zip(predicted, targets)))

    def f1(self, predicted: List[str], targets: List[str]):
        return list(map(lambda pair: calculate_f1_generation(pair[1], pair[0]), zip(predicted, targets)))
