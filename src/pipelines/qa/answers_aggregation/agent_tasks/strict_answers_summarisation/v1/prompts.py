# == Prompts in English ==

EN_SSUBASUMM_SYSTEM_PROMPT = \
    '''
Given a question, associated search-queries and finded information based on them, you are asked to answer this given question only based on these knowledge. If there is no relevant information for generating the suitable answer then you should generate the following: "<|NotEnoughtInfo|>". Before generating the answer you should present your chain of thoughts.

The format you must match for generating response is presented below:
[Chain of thoughts]
<chain-of-thoughts>
[Answer]
<final-answer>
,where <chain-of-thoughts> is your reasoning path based on given question, search-queries and finded information that concludes to the answer and <final-answer> is your final answer to the question.
'''

EN_SSUBASUMM_USER_PROMPT = \
    '''
[Base Question]
{query}

{search_info}
'''

EN_SSUBASUMM_ASSISTANT_PROMPT = \
    '''
[Chain of thoughts]
'''

# == Prompts in Russian ==

RU_SSUBASUMM_SYSTEM_PROMPT = \
    '''
На основании исходного пользовательского вопроса, связанных с ним поисковых запросов и найденной по ним информации вы должны сгенерировать ответ на этот исходный вопрос, при этом основываясь только на заданном набор знаний. Если в заданном наборе нет релевантной информации для формирования правильного/корректного ответа, то вы должны сгенерировать следующее: "<|NotEnoughtInfo|>". Перед генерацией финального ответа вы должны представить свою цепочку рассуждений.

Ответ должен быть сформирован в следующем формате:
[Chain of thoughts]:
<цепочка рассуждений>
[Answer]:
<финальный ответ>
, где <цепочка рассуждений> — это ваш путь рассуждений, основанный на исходном пользовательском вопросе, поисковых запросах и найденной на их основе информации, который приводит к финальному ответу, а <финальный ответ> — ваш окончательный ответ на исходный вопрос.
'''

RU_SSUBASUMM_USER_PROMPT = \
    '''
[Base Question]:
{query}

{search_info}
'''

RU_SSUBASUMM_ASSISTANT_PROMPT = \
    '''
[Chain of thoughts]:
'''
