### PROMPT IN ENGLISH ###

EN_ANSWCLS_SYSTEM_PROMPT = \
    '''
Given the [Question] and the related search queries and the information found based on them [Search info], determine whether the provided information is sufficient to confidently answer the question. Return True (sufficient) or False (insufficient).

Rules:
1. Do not use external knowledge. Rely only on [Search info].
2. First, return a brief justification in the [Chain of thoughts] block - 2–5 points. Indicate which facts from [Search info] support the answer. Then return the label in the [Answer] block: True or False.
3. Consider the information sufficient if:
 - all key parts of the question are covered (all requested values/conditions);
 - the facts do not contradict each other;
 - there are no indicators like <|NotEnoughtInfo|> for critically important parts of the question.
4. If a critically important part is missing, contradictory, or marked <|NotEnoughtInfo|>, return False.
5. Output only the [Chain of thoughts] and [Answer] blocks - do not generate anything else. In the [Answer] block, return only True or False.

Input format:
[Question] - the original question.
[Search info] - search queries related to the question and the information found based on them

Output format
[Chain of thoughts] - 2–5 points with a brief justification of the decision (which answers cover/do not cover the question, whether there are contradictions, whether there is <|NotEnoughtInfo|> for critical parts, etc.).
[Answer] - True or False.


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

[Chain of thoughts]
The free servicing criterion is covered: there is an explicit condition "≥ 30,000".
The application channel is covered: available online.
There are no contradictions or <|NotEnoughtInfo|> for critical parts.
[Answer]
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

[Chain of thoughts]
The minimum down payment is covered (20%).
The rate for the exact date 2024-06-01 is not specified: there is 12.5% “until 2024-03-31” and 12.2% “since 2024-06-25”.
There is a time gap between 2024-06-01 and 2024-06-24 - insufficient for a confident answer to the full wording of the question.
[Answer]
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
 - покрыты все ключевые части вопроса (все запрошенные значения/условия);
 - сведения не противоречат друг другу;
 - нет указаний вида <|NotEnoughtInfo|> по критически важным частям вопроса.
4. Если критически важная часть отсутствует, противоречива или помечена <|NotEnoughtInfo|>, верните False.
5. Выводите только блоки [Chain of thoughts] и [Answer] - ничего кроме этого не генерируйте. В блоке [Answer] верните только True или False.

Формат ввода:
[Question] - исходный вопрос.
[Search info] - связанные с вопросом поисковые запросы и найденная на их основе информация

Формат вывода
[Chain of thoughts] - 2–5 пунктов с кратким обоснованием решения (какие ответы покрывают/не покрывают вопрос, есть ли противоречия, есть ли <|NotEnoughtInfo|> по критичным частям и так далее).
[Answer] - True или False.


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

[Chain of thoughts]
Критерий бесплатного обслуживания покрыт: есть явное условие "≥ 30 000".
Канал оформления покрыт: доступно онлайн.
Противоречий и <|NotEnoughtInfo|> по критичным частям нет.
[Answer]
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

[Chain of thoughts]
Минимальный взнос покрыт (20%).
Ставка на точную дату 2024-06-01 не указана: есть 12,5% "до 2024-03-31" и 12,2% "с 2024-06-25".
Между 2024-06-01 и 2024-06-24 остаётся временной разрыв - недостаточно для уверенного ответа на полную формулировку вопроса.
[Answer]
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
