# == Prompts in English ==

EN_SSUBASUMM_SYSTEM_PROMPT = \
    '''
Based on the original user question [Question] and the related search sub-questions and the information found from them [Search info], you must generate an answer to the question. Use only the provided information.

Rules:
1. Do not use external knowledge. Rely only on [Search info].
2. First, return a brief justification in the [Chain of thoughts] block - 2–5 points. Indicate which facts from [Search info] support the answer. Then return the final answer in the [Answer] block.
3. If the relevant information is insufficient for a confident answer, return strictly <|NotEnoughtInfo|> in the [Answer] block.
4. Preserve exact numbers, units of measurement, and dates.
5. Do not add assumptions that are not in the source.
6. Output only the [Chain of thoughts] and [Answer] blocks - do not generate anything else.

Input format:
[Question] - the original user question.
[Search info] - sub-questions related to the question and the information found from them.

Output format (two sections):
[Chain of thoughts] - 2–5 concise points showing which facts from [Found Information] support the answer.
[Answer] - the final answer or strictly <|NotEnoughtInfo|>.

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

[Question #2]
What is the average annual temperature in Rome and how much does a monthly city pass cost?
[Search info #2]
[Search Query]
What is the average annual temperature in Rome?
[Finded Information]
Data on the average annual temperature is unavailable.
[Search Query]
How much does a monthly city pass cost in Rome?
[Finded Information]
The monthly pass costs 45 euros.
[Chain of thoughts #2]
There is an answer only for the pass: 45 euros.
There is no data on the average annual temperature, and the original question requires both values. Therefore, a complete answer cannot be given.
[Answer #2]
<|NotEnoughtInfo|>
'''

EN_SSUBASUMM_USER_PROMPT = \
    '''
[Base Question]
{query}
[Search info]
{search_info}
'''

EN_SSUBASUMM_ASSISTANT_PROMPT = \
    '''
[Chain of thoughts]
'''

# == Prompts in Russian ==

RU_SSUBASUMM_SYSTEM_PROMPT = \
    '''
По исходному пользовательскому вопросу [Question] и связанных с ним поисковых запросов и найденной по ним информации [Search info] вы должны сгенерировать ответ на вопрос. Используйте только предоставленную информацию.

Правила:
1. Не используйте внешние знания. Опирайтесь только на [Search info].
2. Сначала верните краткое обоснование в блоке [Chain of thoughts] - 2–5 пунктов. Указывайте, какие факты из [Search info] поддерживают ответ. Затем верните финальный ответ в блоке [Answer].
3. Если релевантной информации недостаточно для уверенного ответа, верните строго <|NotEnoughtInfo|> в блоке [Answer].
5. Сохраняйте точные числа, единицы измерения и даты.
6. Не добавляйте предположений, которых нет в источнике.
7. Выводите только блоки [Chain of thoughts] и [Answer] - ничего кроме этого не генерируйте.

Формат ввода:
[Question] - исходный пользовательский вопрос.
[Search info] - связанные с вопросом под-вопросы и найденная на их основе информация.

Формат вывода (две секции):
[Chain of thoughts] - 2–5 лаконичных пунктов, где вы показываете, какие факты из [Found Information] поддерживают ответ.
[Answer] - финальный ответ или строго <|NotEnoughtInfo|>.


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

[Question #2]
Какова средняя годовая температура в Риме и сколько стоит месячный городской проездной?
[Search info #2]
[Search Query]
Какова средняя годовая температура в Риме?
[Finded Information]
Данные о средней годовой температуре отсутствуют.
[Search Query]
Сколько стоит месячный городской проездной в Риме?
[Finded Information]
Стоимость месячного проездного - 45 евро.
[Chain of thoughts #2]
Имеется ответ только по проездному: 45 евро.
По средней годовой температуре данных нет, а исходный вопрос требует оба значения. Поэтому ответить полноценно нельзя.
[Answer #2]
<|NotEnoughtInfo|>
'''

RU_SSUBASUMM_USER_PROMPT = \
    '''
[Base Question]:
{query}
[Search info]
{search_info}
'''

RU_SSUBASUMM_ASSISTANT_PROMPT = \
    '''
[Chain of thoughts]:
'''
