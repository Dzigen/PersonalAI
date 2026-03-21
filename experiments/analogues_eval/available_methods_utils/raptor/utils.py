import sys
REL_RAPTOR_PATH="experiments/analogues_eval/available_methods_utils/raptor/method_source"
RAPTOR_SOURCE_PATH1=f"/home/workspace/{REL_RAPTOR_PATH}" # TO CHANGE
RAPTOR_SOURCE_PATH2=f"/home/m.menschikov/workspace/personal_ai/Personal-AI/{REL_RAPTOR_PATH}" # TO CHANGE
sys.path.insert(0, RAPTOR_SOURCE_PATH1)
sys.path.insert(0, RAPTOR_SOURCE_PATH2)

import openai
from tenacity import retry, stop_after_attempt, wait_random_exponential

from raptor import BaseSummarizationModel
from raptor import BaseQAModel


class CustomSummarizationModel(BaseSummarizationModel):
    def __init__(self, model_name: str, base_url: str):
        self.client = openai.OpenAI(api_key="ollama", base_url=base_url)
        self.model_name = model_name

    @retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(6))
    def summarize(self, context, max_tokens=500):
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {
                    "role": "user",
                    "content": f"Write a summary of the following, including as many key details as possible: {context}:",
                },
            ],
            temperature=0,
            top_p=1,
            max_tokens=max_tokens,
        )

        return response.choices[0].message.content

class CustomQAModel(BaseQAModel):
    def __init__(self, model_name: str, base_url: str):
        self.client = openai.OpenAI(api_key="ollama", base_url=base_url)
        self.model_name = model_name

    @retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(6))
    def answer_question(self, context, question, max_tokens=150, stop_sequence=None):
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": "You are Question Answering Portal"},
                {
                    "role": "user",
                    "content": f"Given Context: {context} Give the best full answer amongst the option to question {question}",
                },
            ],
            temperature=0,
            top_p=1,
            max_tokens=max_tokens
        )

        return response.choices[0].message.content.strip()
