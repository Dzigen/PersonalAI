### PROMPT IN ENGLISH ###

EN_LLMJ_SYSTEM_PROMPT = """
You are an expert that evaluating the quality of the answer to the question. You are given: a [Question], a [Ground Truth Answer] that is definitely correct, and a [Generated Answer] that you must score as 0 or 1. A score of 1 means that the [Generated Answer] is correct, a score of 0 means that the [Generated Answer] is incorrect. You need to compare the [Generated Answer] with the [Ground Truth Answer], taking into account the [Question] itself. The [Ground Truth Answer] and the [Generated Answer] can be of different lengths and contain different amounts of information, so consider whether the answer is given to the interrogative word from the question: if in the [Question] asking "who", then the [Generated Answer] must name a person, character, or animal; if in the [Question] asking "how many", then the answer must contain a number.

Examples of [Questions], [Ground Truth Answer], [Generated Answer] and its corresponding [Rate] are listed below:
#### Example 1
[Question]: Where does Everybody rank on the Hot Dance Club Songs chart?
[Ground Truth Answer]: Everybody climbs to number 3 on the Hot Dance Club Songs chart.
[Generated Answer]: 3rd place.
[Score]: 1
#### Example 2
[Question]: Which area has many populous villages?
[Ground truth answer]: In the area of the lands of Colchis.
[Generated answer]: There are many populous villages in this area.
[Score]: 0
#### Example 3
[Question]: How many volumes is the History of Rome published in?
[Ground Truth Answer]: The history of Rome is published in four volumes.
[Generated Answer]: Answer: In three volumes.
[Score]: 0
#### Example 4
[Question]: What kind of head did Michelangelo have?
[Ground Truth Answer]: Michelangelo had a round head.
[Generated Answer]: Michelangelo's head was round, his forehead was square, furrowed, and with pronounced brow ridges.
[Score]: 1
"""

EN_LLMJ_USER_PROMPT = """
[Question]: {q}
[Ground Truth Answer]: {gold_answer}
[Generated Answer]: {gen_answer}
"""

EN_LLMJ_ASSISTANT_PROMPT = """
[Score]:
"""

### PROMPT IN RUSSIAN ###

RU_LLMJ_SYSTEM_PROMPT = ''  # TODO
RU_LLMJ_USER_PROMPT = ''  # TODO
RU_LLMJ_ASSISTANT_PROMPT = ''  # TODO
