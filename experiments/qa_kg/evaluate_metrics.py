# Source: https://amitness.com/2020/08/information-retrieval-evaluation/

#Retrieval metrics
# - mAP
# - MRR
# - precision
# - recall
# - f1
#Reader metrics
# - BLEU presision
# - ROUGE recall
# - METEOR f1

from torchmetrics.text.rouge import ROUGEScore
from torchmetrics.text import BLEUScore
from evaluate import load
import evaluate
import numpy as np
from typing import List
from tqdm import tqdm
from torchmetrics.text.bert import BERTScore
from Levenshtein import distance as levenshtain_distance

class ReaderMetrics:
    def __init__(self, base_dir, model_path):
        self.rouge_obj = ROUGEScore()
        self.bleu1_obj = BLEUScore(n_gram=1)
        self.bleu2_obj = BLEUScore(n_gram=2)
        print("Loading Meteor...")
        self.meteor_obj = evaluate.load(f"{base_dir}/src/utils/metrics/meteor")
        print("Loading ExactMatch")
        self.em_obj = evaluate.load(f"{base_dir}/src/utils/metrics/exact_match")
        self.bertscore_obj = BERTScore(f"{base_dir}/models/{model_path}", return_hash=True)

    def bertscore(self, predicted: List[str], targets: List[str]):
        output = self.bertscore_obj(predicted, targets)
        output['precision'] = round(float(output['precision'].mean()), 5)
        output['recall'] = round(float(output['recall'].mean()), 5)
        output['f1'] = round(float(output['f1'].mean()), 5)

        return output

    def rougel(self, predicted: List[str], targets: List[str]):
        return [self.rouge_obj(
            predicted[i], targets[i])['rougeL_fmeasure']
                 for i in range(len(targets))]

    def bleu1(self, predicted: List[str], targets: List[str]):
        return [self.bleu1_obj(
            [predicted[i]], [[targets[i]]])
                 for i in range(len(targets))]

    def bleu2(self, predicted: List[str], targets: List[str]):
        return [self.bleu2_obj(
            [predicted[i]], [[targets[i]]])
                 for i in range(len(targets))]

    def meteor(self, predicted: List[str], targets: List[str]):
        return [self.meteor_obj.compute(
            predictions=[predicted[i]], references=[targets[i]])['meteor']
                 for i in range(len(targets))]

    def exact_match(self, predicted: List[str], targets: List[str]):
        return [self.em_obj.compute(
            predictions=[predicted[i]], references=[targets[i]], ignore_case=True, ignore_punctuation=True)["exact_match"]
                for i in range(len(targets))]

    def levenshtain_score(self, predicted: List[str], targets: List[str]):
        return list(map(lambda pair: levenshtain_distance(pair[1], pair[0]), zip(predicted, targets)))
