# == Prompts in English ==

EN_CSUBASUMM_SYSTEM_PROMPT = \
    '''
Based on the original user question [Question] and the related search sub-questions and the information found from them [Search info], you must generate an answer to the question.

Rules:
1. First, return a brief justification in the [Chain of thoughts] block - 2–5 points. Indicate which facts from [Search info] support the answer. Then return the final answer in the [Answer] block.
2. Preserve exact numbers, units of measurement, and dates.
3. Output only the [Chain of thoughts] and [Answer] blocks - do not generate anything else.
4. Return our response in english.

Input format:
[Question] - the original user question.
[Search info] - sub-questions related to the question and the information found from them.
Output format (two sections):
[Chain of thoughts] - 2–5 concise points showing which facts from [Found Information] support the answer.
[Answer] - the final answer.

Examples:

[Question #1]
What are the requirements and the annual maintenance cost for the "Premium" package in 2024?
[Search info #1]
[Search Query]
What is the annual maintenance cost of the "Premium" package in 2024?
[Finded Information]
The annual maintenance cost is 4,990. The tariff has been in effect since 2024-01-01.
[Search Query]
What documents are required to apply for the "Premium" package?
[Finded Information]
A passport and TIN are required. No additional documents are requested.
[Search Query]
Are there any active promotions for the "Premium" package in 2024?
[Finded Information]
There are no active promotions for 2024.
[Chain of thoughts #1]
For the cost sub-question: 4,990 is specified, in effect since 2024-01-01. Therefore, the cost in 2024 is 4,990.
For the documents sub-question: a passport and TIN are required; no other documents are needed.
For the promotions sub-question: there are no discounts in 2024, therefore the price does not decrease.
[Answer #1]
The cost in 2024 is 4,990; to apply you need a passport and TIN.
'''

EN_CSUBASUMM_USER_PROMPT = \
    '''
[Base Question]
{query}
[Search info]
{search_info}
'''

EN_CSUBASUMM_ASSISTANT_PROMPT = \
    '''
[Chain of thoughts]
'''

# == Prompts in Russian ==

RU_CSUBASUMM_SYSTEM_PROMPT = \
    '''
По исходному пользовательскому вопросу [Question] и связанных с ним поисковых запросов и найденной по ним информации [Search info] вы должны сгенерировать ответ на вопрос.

Правила:
1. Сначала верните краткое обоснование в блоке [Chain of thoughts] - 2–5 пунктов. Указывайте, какие факты из [Search info] поддерживают ответ. Затем верните финальный ответ в блоке [Answer].
2. Сохраняйте точные числа, единицы измерения и даты.
3. Выводите только блоки [Chain of thoughts] и [Answer] - ничего кроме этого не генерируйте.
4. Верни свой ответ на русском языке.

Формат ввода:
[Question] - исходный пользовательский вопрос.
[Search info] - связанные с вопросом под-вопросы и найденная на их основе информация.
Формат вывода (две секции):
[Chain of thoughts] - 2–5 лаконичных пунктов, где вы показываете, какие факты из [Found Information] поддерживают ответ.
[Answer] - финальный ответ.

Примеры:

[Question #1]
Каковы требования и стоимость годового обслуживания для пакета "Премиум" в 2024 году?
[Search info #1]
[Search Query]
Какова стоимость годового обслуживания пакета "Премиум" в 2024 году?
[Finded Information]
Стоимость годового обслуживания - 4 990. Тариф действует с 2024-01-01.
[Search Query]
Какие документы требуются для оформления пакета "Премиум"?
[Finded Information]
Требуются паспорт и ИНН. Дополнительные документы не запрашиваются.
[Search Query]
Есть ли действующие акции на пакет "Премиум" в 2024 году?
[Finded Information]
Действующих акций на 2024 год нет.
[Chain of thoughts #1]
По под-вопросу о стоимости: указано 4 990, действует с 2024-01-01. Значит стоимость в 2024 году - 4 990.
По под-вопросу о документах: требуются паспорт и ИНН; иных документов не нужно.
По под-вопросу об акциях: в 2024 году скидок нет, значит цена не уменьшается.
[Answer #1]
Стоимость в 2024 году - 4 990; для оформления нужны паспорт и ИНН.
'''

RU_CSUBASUMM_USER_PROMPT = \
    '''
[Base Question]:
{query}
[Search info]
{search_info}
'''

RU_CSUBASUMM_ASSISTANT_PROMPT = \
    '''
[Chain of thoughts]:
'''
