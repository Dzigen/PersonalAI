EN_ANSWCLS_SYSTEM_PROMPT = \
    '''
Given a question, associated search-queries and finded information based on them, you are asked to determine whether it’s sufficient for you to answer this question based on a given knowledge. Answer 'Yes' or 'No'. Before generating the answer you should present your chain of thoughts.

The format you must match for generating response is presented below:
[Chain of thoughts]
<chain-of-thoughts>
[Answer]
<final-answer>
,where <chain-of-thoughts> is your reasoning path based on given question, search-queries and finded information that concludes to the answer and <final-answer> is your Yes/No-answer.
'''

EN_ANSWCLS_USER_PROMPT = \
    '''
[Question]
{query}

{search_info}
'''

EN_ANSWCLS_ASSISTANT_PROMPT = \
    '''
[Chain of thoughts]
'''

RU_ANSWCLS_SYSTEM_PROMPT = \
    '''
Учитывая вопрос, связанные с ним поисковые запросы и найденную на их основе информацию, вам предлагается определить, достаточно ли для ответа на этот вопрос имеющихся знаний. Ответьте «Да» или «Нет». Прежде чем сформулировать ответ, необходимо сгенерировать свою цепочку рассуждений.

Формат, которому необходимо следовать для формирования ответа, представлен ниже:
[Chain of thoughts]
<цепочка рассуждений>
[Answer]
<финальный ответ>
,где <цепочка рассуждений> — это ваш путь рассуждений, основанный на заданном вопросе, поисковых запросах и найденной на их основе информации информации, который приводит к ответу, а <окончательный ответ> — ваш Да/Нет-ответ .
'''

RU_ANSWCLS_USER_PROMPT = \
    '''
[Question]
{query}

{search_info}
'''
RU_ANSWCLS_ASSISTANT_PROMPT = \
    '''
[Chain of thoughts]
'''
