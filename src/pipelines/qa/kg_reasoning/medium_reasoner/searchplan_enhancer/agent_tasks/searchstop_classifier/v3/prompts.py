### PROMPT IN ENGLISH ###

EN_SEARCHSCLS_SYSTEM_PROMPT = \
    '''
Given a [Question], associated search-plan and finded information at current moment based on specific search-queries, you are asked to determine whether [Next search-plan queries at now] (1) are approprite to find relevant information for a [Question] and (2) do not duplicate previous [Complited search-plan queries] OR information search for a given [Question], based on given plan, should be stoped, because requested knowledge can not be found. Answer 'True' if [Next search-plan queries at now] are appropriate for infromation search and do not duplicate complited search-queries, otherwise 'False'. Before generating the answer you should present your chain of thoughts.

Rules:
1. If [Complited search-plan queries] is empty, then return 'True'.
2. Return your response in english.

The format you must match for generating response is presented below:
[Chain of thoughts]
<chain-of-thoughts>
[Answer]
<final-answer>
,where <chain-of-thoughts> is your reasoning path based on given question, search-plan and finded information at now that concludes to the answer and <final-answer> is your True/False-answer.
'''

EN_SEARCHSCLS_USER_PROMPT = \
    '''
[Question]
{query}

[Complited search-plan queries]
{complited_squeries}

[Next search-plan queries at now]
{next_squeries}
'''

EN_SEARCHSCLS_ASSISTANT_PROMPT = \
    '''
[Chain of thoughts]
'''

### PROMPT IN RUSSIAN ###

RU_SEARCHSCLS_SYSTEM_PROMPT = \
    '''
Имея [Question], соответствующий план поиска и информацию, уже найденную с помощью выполненных ранее поисковых запросов, определите: (1) подходят ли [Next search-plan queries at now] для нахождения релевантной информации по данному [Question] и (2) не дублируют ли они [Complited search-plan queries]; либо же следует прекратить поиск информации по данному [Question] (согласно плану), так как искомые сведения найти невозможно. Ответьте 'True', если [Next search-plan queries at now] подходят для поиска информации и не дублируют уже выполненные запросы; в противном случае ответьте 'False'. Перед тем, как сгенерировать ответ, необходимо представить свою цепочку рассуждений.

Правила:
1. Если [Complited search-plan queries] пустой, то верни 'True'.
2. Верни свой ответ на русском языке.

Формат, который необходимо использовать для генерации ответа, представлен ниже:
[Chain of thoughts]
<цепочка рассуждений>
[Answer]
<финальный ответ>
, где <цепочка рассуждений> — это ваш путь рассуждений, основанный на заданном вопросе, плане поиска и найденной на данный момент информации, который приводит к ответу, а <финальный ответ> — ваш True/False-ответ .
'''

RU_SEARCHSCLS_USER_PROMPT = \
    '''
[Question]
{query}

[Complited search-plan queries]
{complited_squeries}

[Next search-plan queries at now]
{next_squeries}
'''

RU_SEARCHSCLS_ASSISTANT_PROMPT = \
    '''
[Chain of thoughts]
'''
