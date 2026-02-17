import sys
sys.path.insert(0, "/home/workspace/experiments/analogues_eval/available_methods_utils/raptor/method_source")

from raptor import BaseSummarizationModel
from raptor import BaseQAModel

class CustomSummarizationModel(BaseSummarizationModel):
    def __init__(self):
        # Initialize your model here
        pass

    def summarize(self, context, max_tokens=150):
        # Implement your summarization logic here
        # Return the summary as a string
        summary = "Your summary here"
        return summary

class CustomQAModel(BaseQAModel):
    def __init__(self):
        # Initialize your model here
        pass

    def answer_question(self, context, question):
        # Implement your QA logic here
        # Return the answer as a string
        answer = "Your answer here"
        return answer
