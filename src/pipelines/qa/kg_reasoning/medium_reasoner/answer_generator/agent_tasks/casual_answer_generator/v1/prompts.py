### PROMPT IN ENGLISH ###

EN_CANSWGEN_SYSTEM_PROMPT = \
    '''
Given the [Question] and the related search queries and the information found based on them [Search info], you must generate an answer to the question.

Rules:
1. First, return a brief justification in the [Chain of thoughts] block - 2–5 points. Indicate which facts from [Search info] support the answer. Then return the [Answer] block - the final answer.
2. Preserve exact numbers, units of measurement, and dates.
3. Output only the [Chain of thoughts] and [Answer] blocks - do not generate anything else.

Input format:
[Question] - the original question.
[Search info] - search queries related to the question and the information found based on them
Output format
[Chain of thoughts] - 2–5 points referring to the answers from [Search info].
[Answer] - the final answer.

Examples:

[Question #1]
Is international roaming available in the "Global" plan on 2025-03-01, and how much does 1 GB cost in Europe?
[Search info #1]
[Search Query]
Is international roaming available in the "Global" plan on 2025-03-01?
[Finded Information]
International roaming is included. The service has been active since 2025-02-15.
[Search Query]
How much does 1 GB of mobile internet cost in Europe in the "Global" plan?
[Finded Information]
1 GB in Europe costs 6 euros with roaming enabled; charged per megabyte within the bundle.
[Chain of thoughts #1]
For sub-question #0: roaming is included, active since 2025-02-15 - available on 2025-03-01.
For sub-question #1: the price is specified - 6 euros per 1 GB in Europe.
Both components of the original question are covered, no contradictions.
[Answer #1]
International roaming in the "Global" plan is available; 1 GB in Europe costs 6 euros.
'''

EN_CANSWGEN_USER_PROMPT = \
    '''
[Question]
{query}
[Search info]
{search_info}
'''

EN_CANSWGEN_ASSISTANT_PROMPT = \
    '''
[Chain of thoughts]
'''

### PROMPT IN RUSSIAN ###

RU_CANSWGEN_SYSTEM_PROMPT = \
    '''
По вопросу [Question] и связанным с ним поисковым запросам и найденным на их основе информации [Search info] вы должны сгенерировать ответ на вопрос.

Правила:
1. Сначала верните краткое обоснование в блоке [Chain of thoughts] - 2–5 пунктов. Указывайте, какие факты из [Search info] поддерживают ответ. Затем верните блок [Answer] - финальный ответ.
2. Сохраняйте точные числа, единицы измерения и даты.
3. Выводите только блоки [Chain of thoughts] и [Answer] - ничего кроме этого не генерируйте.

Формат ввода:
[Question] - исходный вопрос.
[Search info] - связанные с вопросом поисковые запросы и найденная на их основе информация
Формат вывода
[Chain of thoughts] - 2–5 пунктов, ссылающихся на ответы из [Search info].
[Answer] - финальный ответ.

Примеры:

[Question #1]
Доступен ли международный роуминг в тарифе "Глобал" на 2025-03-01 и сколько стоит 1 ГБ в Европе?
[Search info #1]
[Search Query]
Доступен ли международный роуминг в тарифе "Глобал" на 2025-03-01?
[Finded Information]
Международный роуминг включён. Услуга активна с 2025-02-15.
[Search Query]
Сколько стоит 1 ГБ мобильного интернета в Европе в тарифе "Глобал"?
[Finded Information]
1 ГБ в Европе стоит 6 евро при подключённом роуминге; списание помегабайтно в рамках пакета.
[Chain of thoughts #1]
По под-вопросу #0: роуминг включён, активен с 2025-02-15 - на 2025-03-01 доступен.
По под-вопросу #1: стоимость указана - 6 евро за 1 ГБ в Европе.
Оба компонента исходного вопроса покрыты, противоречий нет.
[Answer #1]
Международный роуминг в тарифе "Глобал" доступен; 1 ГБ в Европе обойдется в 6 евро.
'''

RU_CANSWGEN_USER_PROMPT = \
    '''
[Question]
{query}
[Search info]
{search_info}
'''

RU_CANSWGEN_ASSISTANT_PROMPT = \
    '''
[Chain of thoughts]
'''
