# == Prompts in English ==

EN_DC_SYSTEM_PROMPT = \
    '''
Given a question you are asked to determine whether it can be decomposed on several independent questions that can be answered in isolation to eachother. Answer 'True' or 'False'. Before generating the answer you should present your chain of thoughts.

The format you must match for generating response is presented below:
[Chain of thoughts]
<chain-of-thoughts>
[Answer]
<final-answer>
,where <chain-of-thoughts> is your reasoning path based on given question that concludes to the answer and <final-answer> is your True/False-answer.
'''

EN_DC_USER_PROMPT = \
    '''
[Base question]
{query}
'''
EN_DC_ASSISTANT_PROMPT = \
    '''
[Chain of thoughts]
'''

# == Prompts in Russian ==

RU_DC_SYSTEM_PROMPT = \
    '''
Вам должны определить: можно ли разбить заданный вопрос на несколько независимых простых вопросов, на которые можно ответить независимо друг от друга. Сгенерируйте «True» или «False».
Перед тем, как сгенерировать финальный ответ, вы должны представить/сгенерировать свою цепочку рассуждений. Не генерируйте ничего лишнего.

Формат, которому необходимо следовать для генерации ответа, представлен ниже:
[Chain of thoughts]
<цепочка рассуждений>
[Answer]
<окончательный ответ>
, где <цепочка рассуждений> — это ваш путь рассуждений, основанный на заданном вопросе и приводящий к ответу, а <окончательный ответ> — ваш True/False-ответ.
'''

RU_DC_USER_PROMPT = \
    '''
[Base question]
{query}
'''

RU_DC_ASSISTANT_PROMPT = \
    '''
[Chain of thoughts]
'''
