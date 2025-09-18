### PROMPT IN ENGLISH ###

EN_CAGEN_SYSTEM_PROMPT = \
    """
Given a question and finded information based on it, you are asked to recognize and summarize all relevant information, that can be used as a part of suitable context to generate the answer. If there is no relevant information in a given finded information, then you should generate the following: "<|NoRelevantInfo|>".
"""

EN_CAGEN_USER_PROMPT = \
    """
[Question]:
{q}
[Finded Information]:
{c}
"""

EN_CAGEN_ASSISTANT_PROMPT = \
    """
[Relevant Summary]:
"""

### PROMPT IN RUSSIAN ###

RU_CAGEN_SYSTEM_PROMPT = \
    """
На основе вопроса и найденной по нему информации вам предлагается определить и обобщить всю релевантную информацию, которая может быть использована в качестве части контекста для формирования ответа на данный вопрос. Если в найденной информации нет релевантной, следует сгенерировать следующее: "<|NoRelevantInfo|>".
"""

RU_CAGEN_USER_PROMPT = \
    """
[Question]:
{q}
[Finded Information]:
{c}
"""

RU_CAGEN_ASSISTANT_PROMPT = \
    """
[Relevant Summary]:
"""
