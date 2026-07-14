import sys
sys.path.insert(0, "../../")

from metrics.my_ragas.RagasMetrics import RagasMetrics
from time import time

ragas = RagasMetrics()

data = {
    "user_input": [
        "What is the capital of France?",
        "Who wrote the play Hamlet?",
        "What is 2+2?",
        "What is 3+3?"
    ],
    "response": [
        "The capital of France is Paris.",
        "Hamlet was written by William Shakespeare.",
        "2+2=4",
        "3+3=6"
    ],
    "retrieved_contexts": [
        ["Paris is the capital and most populous city of France."], # Must be a list of strings
        ["Hamlet is a tragedy written by William Shakespeare at an uncertain date."],
        ["2+2=4", "3+3=6"],
        ["2+2=4", "3+3=6"]
    ],
    "reference": [
        "Paris.",
        "William Shakespeare.",
        "2+2=4",
        "3+3=6"
    ]
}

print(data)

s_time = time()
results = ragas.evaluate(**data)
e_time = time()
print(e_time - s_time)

print(results)
