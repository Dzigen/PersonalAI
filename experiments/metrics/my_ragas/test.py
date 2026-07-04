import sys
sys.path.insert(0, "../../")

from metrics.my_ragas.RagasMetrics import RagasMetrics
from time import time

ragas = RagasMetrics()

data = {
    "user_input": [
        "What is the capital of France?",
        "Who wrote the play Hamlet?"
    ],
    "response": [
        "The capital of France is Paris.",
        "Hamlet was written by William Shakespeare."
    ],
    "retrieved_contexts": [
        ["Paris is the capital and most populous city of France."], # Must be a list of strings
        ["Hamlet is a tragedy written by William Shakespeare at an uncertain date."]
    ],
    "reference": [
        "Paris.",
        "William Shakespeare."
    ]
}

print(data)

s_time = time()
results = ragas.evaluate(**data)
e_time = time()
print(e_time - s_time)

print(results)
