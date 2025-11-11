### PROMPT IN ENGLISH ###

EN_ANSWGEN_SYSTEM_PROMPT = \
    '''
Given the [Question] and the related search queries and the information found based on them [Search info], you must generate an answer to the question. Use only the provided data.

Rules:
1. Do not use external knowledge. Rely only on [Search info].
2. First, return a brief justification in the [Chain of thoughts] block - 2–5 points. Indicate which facts from [Search info] support the answer. Then return the [Answer] block - the final answer.
3. If the information is insufficient for a confident answer, return strictly <|NotEnoughtInfo|> in [Answer].
4. Preserve the language and style of the original [Question].
5. Preserve exact numbers, units of measurement, and dates.
6. Do not add assumptions or conclusions that are not in the source.
7. Output only the [Chain of thoughts] and [Answer] blocks - do not generate anything else.

Input format:
[Question] - the original question.
[Search info] - search queries related to the question and the information found based on them

Output format
[Chain of thoughts] - 2–5 points referring to the answers from [Search info].
[Answer] - the final answer or strictly <|NotEnoughtInfo|>.


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

[Chain of thoughts]
For sub-question #0: roaming is included, active since 2025-02-15 - available on 2025-03-01.
For sub-question #1: the price is specified - 6 euros per 1 GB in Europe.
Both components of the original question are covered, no contradictions.
[Answer]
International roaming in the "Global" plan is available; 1 GB in Europe costs 6 euros.

[Question #2]
Is there a student discount for a membership at the "Pulse" gym, and what is the monthly price with the discount?
[Search info]
[Search Query]
Is a student discount provided at the “Pulse” gym?
[Finded Information]
A student discount is available upon presenting a student ID.

[Search Query]
What is the monthly membership price at "Pulse" with the student discount?
[Finded Information]
<|NotEnoughtInfo|>

[Chain of thoughts]
Sub-question #0 confirms the existence of a student discount.
Sub-question #1 does not provide the price (the <|NotEnoughtInfo|> marker).
The original question requires both the fact of the discount and the specific price - the data is insufficient.
[Answer]
<|NotEnoughtInfo|>
'''

EN_ANSWGEN_USER_PROMPT = \
    '''
[Question]
{query}
[Search info]
{search_info}
'''

EN_ANSWGEN_ASSISTANT_PROMPT = \
    '''
[Chain of thoughts]
'''

### PROMPT IN RUSSIAN ###

RU_ANSWGEN_SYSTEM_PROMPT = \
    '''
По вопросу [Question] и связанным с ним поисковым запросам и найденным на их основе информации [Search info] вы должны сгенерировать ответ на вопрос. Используйте только предоставленные данные.

Правила:
1. Не используйте внешние знания. Опирайтесь только на [Search info].
2. Сначала верните краткое обоснование в блоке [Chain of thoughts] - 2–5 пунктов. Указывайте, какие факты из [Search info] поддерживают ответ. Затем верните блок [Answer] - финальный ответ.
3. Если информации недостаточно для уверенного ответа, верните строго <|NotEnoughtInfo|> в [Answer].
4. Сохраняйте язык и стиль исходного вопроса [Question].
5. Сохраняйте точные числа, единицы измерения и даты.
6. Не добавляйте домыслов и выводов, которых нет в источнике.
7. Выводите только блоки [Chain of thoughts] и [Answer] - ничего кроме этого не генерируйте.

Формат ввода:
[Question] - исходный вопрос.
[Search info] - связанные с вопросом поисковые запросы и найденная на их основе информация

Формат вывода
[Chain of thoughts] - 2–5 пунктов, ссылающихся на ответы из [Search info].
[Answer] - финальный ответ или строго <|NotEnoughtInfo|>.


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

[Chain of thoughts]
По под-вопросу #0: роуминг включён, активен с 2025-02-15 - на 2025-03-01 доступен.
По под-вопросу #1: стоимость указана - 6 евро за 1 ГБ в Европе.
Оба компонента исходного вопроса покрыты, противоречий нет.
[Answer]
Международный роуминг в тарифе "Глобал" доступен; 1 ГБ в Европе обойдется в 6 евро.

[Question #2]
Есть ли скидка для студентов на абонемент в спортзал "Пульс" и какова ежемесячная цена со скидкой?
[Search info]
[Search Query]
Предусмотрена ли студенческая скидка в спортзале "Пульс"?
[Finded Information]
Студенческая скидка действует при предъявлении студенческого билета.

[Search Query]
Какова ежемесячная цена абонемента в "Пульс" со студенческой скидкой?
[Finded Information]
<|NotEnoughtInfo|>

[Chain of thoughts]
Под-вопрос #0 подтверждает наличие студенческой скидки.
Под-вопрос #1 не содержит цены (маркёр <|NotEnoughtInfo|>).
Исходный вопрос требует и факт скидки, и конкретную стоимость - данных недостаточно.
[Answer]
<|NotEnoughtInfo|>
'''

RU_ANSWGEN_USER_PROMPT = \
    '''
[Question]
{query}
[Search info]
{search_info}
'''

RU_ANSWGEN_ASSISTANT_PROMPT = \
    '''
[Chain of thoughts]
'''
