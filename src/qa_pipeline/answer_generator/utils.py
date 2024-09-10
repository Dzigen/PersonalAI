from dataclasses import dataclass, field
from typing import List
from enum import Enum

QUESTION_ANSWERING_USER_PROMPT = """Answer the question, based on provided info by analogy with examples given. Generate chain of thought and then give the final answer in the following format:
### Answer
Chain of thought: ... Final answer: ...
Question 1: Whose opinions from Anthony and Grace about devices are most similar to Faith's?
Info 1: person: Anthony, device: Xiaomi, opinion: hard, feature: maintenance point
person: Anthony, device: mate30pro, opinion: not as good as, feature: signal
person: Anthony, device: iPhone, opinion: not as good as, feature: signal
person: Grace, device: Xiaomi 12, opinion: beat, feature: charging speed
person: Faith, device: Xiaomi, opinion: problem, feature: product control
person: Faith, device: k30s, opinion: not as good, feature: film effect
person: Faith, device: red rice, opinion: not as good, feature: film effect
### Answer 1
Chain of thought 1: The task is to compare Anthony's and Grace's opinions to Faith's opinions about devices. Faith has two types of opinions: "problem" with the Xiaomi device and "not as good" with both k30s and red rice devices. We will look for similar expressions of dissatisfaction from Anthony and Grace. Grace's opinion about Xiaomi 12 is "beat," which is not similar to any of Faith's negative opinions. Anthony's opinions include "hard" for Xiaomi and "not as good as" for mate30pro and iPhone with respect to the signal feature. "Not as good as" matches Faith's "not as good."
Final answer 1: Anthony
Question 2: The majority of speakers have positive, neutral or negative sentiment about signal of Apple?
Info 2: person: Alejandro, time: 15.11.2020, opinion: beats, device: Apple, feature: battery life
person: Jacqueline, time: 30.12.2020, opinion: Nice pictures taken, device: Apple, feature: taking pictures
person: Diego, time: 30.12.2020, opinion: Doesnt overheat, device: Apple, feature: heat radiation
person: Lily, time: 30.12.2020, opinion: Not bad, device: Apple, feature: configuration of other processors
person: Margaret, time: 25.11.2020, opinion: Pictures turn blurry, device: Apple, feature: taking pictures
person: Amber, time: 25.11.2020, opinion: Really unhelpful, device: Apple, feature: sales
person: Jessica, time: 25.11.2020, opinion: Always been strong, device: Apple, feature: signal
person: Bernard, time: 25.11.2020, opinion: No lag, device: Apple, feature: play games
### Answer 2
Chain of thought 2: To determine the sentiment about the signal of Apple, we need to find the opinions specifically related to the "signal" feature of Apple. From the provided info, only Jessica's opinion mentions the signal: "Always been strong." This is a positive sentiment. Since there's only one opinion regarding the signal, the majority sentiment is positive.
Final answer 2: Positive
Question 3: {q}
Info 3: {c}
### Answer 3 """

class ContextType(Enum):
    simple = "simple"
    hyper = "hyper"
    episodic = "episodic"

@dataclass
class QALLMGeneratorConfig:
    user_prompt: str = QUESTION_ANSWERING_USER_PROMPT
    context_type: List[ContextType] = field(default_factory=lambda: 
                                            [ContextType.simple, ContextType.hyper, ContextType.episodic])