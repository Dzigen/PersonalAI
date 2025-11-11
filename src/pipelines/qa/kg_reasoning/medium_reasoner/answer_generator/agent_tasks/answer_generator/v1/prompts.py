### PROMPT IN ENGLISH ###

EN_ANSWGEN_SYSTEM_PROMPT = \
    '''
Given a question, associated search-queries and finded information based on them, you are asked to answer the question only based on these knowledge. If there is no relevant information in a given finded information for generating the suitable answer, then you should generate the following: "<|NotEnoughtInfo|>". Before generating the answer you should present your chain of thoughts.

The format you must match for generating response is presented below:
[Chain of thoughts]
<chain-of-thoughts>
[Answer]
<final-answer>
,where <chain-of-thoughts> is your reasoning path based on given question,search-queries and finded information that concludes to the answer and <final-answer> is your final answer to the question.
'''

EN_ANSWGEN_USER_PROMPT = \
    '''
[Question]
{query}

{search_info}
'''

EN_ANSWGEN_ASSISTANT_PROMPT = \
    '''
[Chain of thoughts]
'''

### PROMPT IN RUSSIAN ###

RU_ANSWGEN_SYSTEM_PROMPT = \
    '''
Имея исходный вопрос, связанные с ним поисковые запросы и найденную на их основе информацию, вам предлагается ответить на исходный вопрос, основываясь только на этих знаниях. Если в найденной информации нет релевантной для формирования подходящего ответа, необходимо сгенерировать следующее: "<|NotEnoughtInfo|>". Перед формированием ответа необходимо представить свою цепочку рассуждений.

Формат, которому необходимо следовать для формирования ответа, представлен ниже:
[Chain of thoughts]
<цепочка рассуждений>
[Answer]
<финальный ответ>
,где <цепочка рассуждений> — это ваш путь рассуждений, основанный на заданном вопросе, поисковых запросах и найденной на их основе информации, которая приводит к ответу, а <финальный ответ> — ваш окончательный ответ на вопрос.
'''

RU_ANSWGEN_USER_PROMPT = \
    '''
[Question]
{query}

{search_info}
'''

RU_ANSWGEN_ASSISTANT_PROMPT = \
    '''
[Chain of thoughts]
'''
