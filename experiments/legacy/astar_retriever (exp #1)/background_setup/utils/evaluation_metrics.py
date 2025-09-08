# Source: https://amitness.com/2020/08/information-retrieval-evaluation/

from torchmetrics.text.rouge import ROUGEScore
from torchmetrics.text import BLEUScore
import evaluate
from typing import List, Dict

#


class ReaderMetrics:
    def __init__(self, base_dir: str):
        self.rouge_obj = ROUGEScore()
        self.bleu1_obj = BLEUScore(n_gram=1)
        self.bleu2_obj = BLEUScore(n_gram=2)
        print("Loading Meteor...")
        self.meteor_obj = evaluate.load(f"{base_dir}/metrics/meteor")
        print("Loading ExactMatch")
        self.em_obj = evaluate.load(f"{base_dir}/metrics/exact_match")

    def rougel(self, predicted: List[str], targets: List[str]) -> List[float]:
        return [self.rouge_obj(
            predicted[i], targets[i])['rougeL_fmeasure']
            for i in range(len(targets))]

    def bleu1(self, predicted: List[str], targets: List[str]) -> List[float]:
        return [self.bleu1_obj(
            [predicted[i]], [[targets[i]]])
            for i in range(len(targets))]

    def bleu2(self, predicted: List[str], targets: List[str]) -> List[float]:
        return [self.bleu2_obj(
            [predicted[i]], [[targets[i]]])
            for i in range(len(targets))]

    def meteor(self, predicted: List[str], targets: List[str]) -> List[float]:
        return [self.meteor_obj.compute(
            predictions=[predicted[i]], references=[targets[i]])['meteor']
            for i in range(len(targets))]

    def exact_match(self, predicted: List[str], targets: List[str]) -> List[float]:
        return [self.em_obj.compute(
            predictions=[predicted[i]], references=[targets[i]], ignore_case=True)["exact_match"]
            for i in range(len(targets))]
