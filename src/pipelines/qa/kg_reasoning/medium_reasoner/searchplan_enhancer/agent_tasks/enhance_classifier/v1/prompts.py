### PROMPT IN ENGLISH ###

EN_ENHCLS_SYSTEM_PROMPT = \
    '''
Given a question, associated search-plan and finded information at current moment based on them (search-queries), you are asked to determine whether next search-queries should be enhanced/modified to find more relevant information and generate more accurate answer. Answer 'True' or 'False'. Before generating the answer you should present your chain of thoughts.

The format you must match for generating response is presented below:
[Chain of thoughts]
<chain-of-thoughts>
[Answer]
<final-answer>
,where <chain-of-thoughts> is your reasoning path based on given question, search-plan and finded information at now that concludes to the answer and <final-answer> is your True/False-answer.
'''

EN_ENHCLS_USER_PROMPT = \
    '''
[Question]
{query}

[Complited search-plan queries]
{complited_squeries}

[Next search-plan queries at now]
{next_squeries}
'''

EN_ENHCLS_ASSISTANT_PROMPT = \
    '''
[Chain of thoughts]
'''

### PROMPT IN RUSSIAN ###

RU_ENHCLS_SYSTEM_PROMPT = \
    '''
Учитывая вопрос, связанный с ним план поиска и найденную на данный момент информацию (поисковые запросы), вам предлагается определить, следует ли улучшить/изменить следующие поисковые запросы для поиска более релевантной информации и получения более точного ответа. Ответьте «True» или «False». Перед тем, как сгенерировать ответ, необходимо представить свою цепочку рассуждений.

Формат, который необходимо использовать для генерации ответа, представлен ниже:
[Chain of thoughts]
<цепочка рассуждений>
[Answer]
<финальный ответ>
, где <цепочка рассуждений> — это ваш путь рассуждений, основанный на заданном вопросе, плане поиска и найденной на данный момент информации, который приводит к ответу, а <финальный ответ> — ваш True/False-ответ .
'''

RU_ENHCLS_USER_PROMPT = \
    '''
[Question]
{query}

[Complited search-plan queries]
{complited_squeries}

[Next search-plan queries at now]
{next_squeries}
'''

RU_ENHCLS_ASSISTANT_PROMPT = \
    '''
[Chain of thoughts]
'''
