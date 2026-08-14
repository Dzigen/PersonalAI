### PROMPT IN ENGLISH ###

EN_ANSWCLS_SYSTEM_PROMPT = \
    '''
Given the [Question] and the related search queries and the information found based on them [Search info], determine whether the provided information is sufficient to confidently answer the question. Return True (sufficient) or False (insufficient).

Rules:
1. Do not use external knowledge. Rely only on [Search info].
2. First, return a brief justification in the [Chain of thoughts] block - 2–5 points. Indicate which facts from [Search info] support the answer. Then return the label in the [Answer] block: True or False.
3. Consider the information sufficient if:
 - all key parts of the question are covered (all requested values/conditions).
4. If a critically important part is missing, then return False.
5. Output only the [Chain of thoughts] and [Answer] blocks - do not generate anything else. In the [Answer] block, return only True or False.
6. Return your response in english.

Input format:
[Question] - the original question.
[Search info] - search queries related to the question and the information found based on them
Output format
[Chain of thoughts] - 2–5 points with a brief justification of the decision (which answers cover/do not cover the question, whether there are contradictions, etc.).
[Answer] - ONLY and STRICTLY "True" or "False". Do not add any descriptions/explanations to your True/False-answer.

Examples:

[Question #1]
Is the "Start" package serviced for free with a monthly turnover of at least 30,000, and is online application available?
[Search info #1]
[Search Query]
Is free servicing of the "Start" package available with a 30,000 monthly turnover?
[Finded Information]
Servicing is free with a turnover of ≥ 30,000 in a calendar month.
[Search Query]
Can the "Start" package be applied for online?
[Finded Information]
Application is available in the mobile app and in the web cabinet.
[Answer #1]
True

[Question #2]
What is the mortgage rate for "New Build" on 2024-06-01, and what is the minimum down payment required?
[Search info #2]
[Search Query]
What is the minimum down payment under the "New Build" program?
[Finded Information]
The minimum down payment is 20% of the property price.
[Search Query]
What is the rate under the "New Build" program in June 2024?
[Finded Information]
Since 2024-06-25 the rate is 12.2% per annum. Previously, until 2024-03-31, the rate was 12.5%.
[Answer #2]
False
'''

EN_ANSWCLS_USER_PROMPT = \
    '''
[Question]
{query}
[Search info]
{search_info}
'''

EN_ANSWCLS_ASSISTANT_PROMPT = \
    '''
[Chain of thoughts]
'''

### PROMPT IN RUSSIAN ###

RU_ANSWCLS_SYSTEM_PROMPT = \
    '''
По вопросу [Question] и связанным с ним поисковым запросам и найденным на их основе информации [Search info] определите, достаточно ли предоставленной информации, чтобы уверенно ответить на вопрос. Верните True (достаточно) или False (недостаточно).

Правила:
1. Не используйте внешние знания. Опирайтесь только на [Search info].
2. Сначала верните краткое обоснование в блоке [Chain of thoughts] - 2–5 пунктов. Указывайте, какие факты из [Search info] поддерживают ответ. Затем верните метку в блоке [Answer]: True или False.
3. Считайте информацию достаточной, если:
 - покрыты все ключевые части вопроса (все запрошенные значения/условия).
4. Если критически важная часть отсутствует или противоречива, тогда верните False.
5. Выводите только блоки [Chain of thoughts] и [Answer] - ничего кроме этого не генерируйте. В блоке [Answer] верните только True или False.
6. Верни свой ответ на русском языке.

Формат ввода:
[Question] - исходный вопрос.
[Search info] - связанные с вопросом поисковые запросы и найденная на их основе информация
Формат вывода
[Chain of thoughts] - 2–5 пунктов с кратким обоснованием решения (какие ответы покрывают/не покрывают вопрос, есть ли противоречия и так далее).
[Answer] - ТОЛЬКО и СТРОГО "True" или "False". Не добавляйте каких-либо дополнительных пояснений к своему True/False-ответу.

Примеры:

[Question #1]
Есть ли бесплатное обслуживание пакета "Старт" при ежемесячном обороте от 30 000 и доступно ли оформление онлайн?
[Search info #1]
[Search Query]
Доступно ли бесплатное обслуживание пакета "Старт" при обороте 30 000 в месяц?
[Finded Information]
Обслуживание бесплатно при обороте ≥ 30 000 в календарном месяце.
[Search Query]
Можно ли оформить пакет "Старт" онлайн?
[Finded Information]
Оформление доступно в мобильном приложении и в веб-кабинете.
[Answer #1]
True

[Question #2]
Какова ставка по ипотеке "Новостройка" на 2024-06-01 и какой минимальный первоначальный взнос требуется?
[Search info #2]
[Search Query]
Какой минимальный первоначальный взнос по программе "Новостройка"?
[Finded Information]
Минимальный первоначальный взнос - 20% от стоимости жилья.
[Search Query]
Какая ставка по программе "Новостройка" в июне 2024?
[Finded Information]
С 2024-06-25 ставка 12,2% годовых. Ранее, до 2024-03-31, ставка составляла 12,5%.
[Answer #2]
False
'''

RU_ANSWCLS_USER_PROMPT = \
    '''
[Question]
{query}
[Search info]
{search_info}
'''
RU_ANSWCLS_ASSISTANT_PROMPT = \
    '''
[Chain of thoughts]
'''
