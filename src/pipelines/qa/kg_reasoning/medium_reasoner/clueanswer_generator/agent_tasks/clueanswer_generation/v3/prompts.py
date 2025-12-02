### PROMPT IN ENGLISH ###

EN_CAGEN_SYSTEM_PROMPT = \
    """
Based on [Question] and [Found Information] your task is to extract and briefly summarize only the relevant facts needed to answer the question.

Rules:
1. Use only the information provided in [Found Information]. Do not use external knowledge.
2. Select only information relevant to the question (facts, dates, quantities, conditions, constraints, etc.). Ignore everything else.
3. If there is no relevant information, return strictly <|NoRelevantInfo|>.
4. Preserve the language and style of the original [Question].
5. Preserve exact numbers, units of measurement, and dates.
6. Do not make inferences or generalizations that are not in the source. Do not add assumptions.
7. Output only the [Relevant Summary] section. Do not generate anything else.

Input format:
[Question] - the original question.
[Found Information] - the discovered text/fact fragments.

Output format (single section):
[Relevant Summary] - a brief summary of the relevant facts or strictly <|NoRelevantInfo|>.


Examples:
[Question #1]
What is the base rate for the "Premier" deposit on 2024-02-01?
[Found Information #1]
(Deposit "Premier", interest rate, 5.5%, t_valid_from=2023-11-01, t_valid_to=2024-01-14)
(Deposit "Premier", interest rate, 6.0%, t_valid_from=2024-01-15)
(Deposit "Premier", required document, Passport)
[Relevant Summary]
As of 2024-02-01 the applicable rate is 6.0% per annum (introduced on 2024-01-15). The archived 5.5% rate was valid until 2024-01-15.

[Question #2]
How long is the warranty for a MacBook Pro in Russia?
[Found Information #2]
(Laptop MacBook Pro, warranty in Russia (months), 12)
(Laptop MacBook Pro, warranty in Europe (months), 24)
(Service centers, listed on, official website)
[Relevant Summary]
The warranty for MacBook Pro in Russia is 12 months.

[Question #3]
What is the height of the "Orin" peak (in meters)?
[Found Information #3]
(Orin Region, seasonal recommendations, June–September)
(Orin Lake, nearby, campsite)
[Relevant Summary]
<|NoRelevantInfo|>

"""

EN_CAGEN_USER_PROMPT = \
    """
[Question]
{q}
[Finded Information]
{c}
"""

EN_CAGEN_ASSISTANT_PROMPT = \
    """
[Relevant Summary]
"""

### PROMPT IN RUSSIAN ###

RU_CAGEN_SYSTEM_PROMPT = \
    """
Ваша задача - по [Question] и [Found Information] выделить и кратко обобщить только релевантные факты для ответа на вопрос.

Правила:
1. Используйте только предоставленную информацию из [Found Information]. Не используйте внешние знания.
2. Выделяйте только релевантную информацию (факты, даты, величины, условия, ограничения и так далее), относящиеся к вопросу. Игнорируйте всё остальное.
3. Если релевантной информации нет, верните строго <|NoRelevantInfo|>.
4. Сохраняйте язык и стиль исходного вопроса [Question]
5. Сохраняйте точные числа, единицы измерения и даты.
6. Не делайте выводов и обобщений, которых нет в источнике. Не добавляйте домыслов.
7. Выводите только секцию [Relevant Summary]. Ничего кроме этого не генерируйте.

Формат ввода:
[Question] - исходный вопрос.
[Found Information] - найденные фрагменты текста/фактов.

Формат вывода (единственная секция):
[Relevant Summary] - краткое обобщение релевантных фактов или строго <|NoRelevantInfo|>.


Примеры:
[Question #1]
Какая базовая ставка по вкладу "Премьер" на 2024-02-01?
[Found Information #1]
(Вклад "Премьер", процентная ставка, 5.5%, t_valid_from=2023-11-01, t_valid_to=2024-01-14)
(Вклад "Премьер", процентная ставка, 6.0%, t_valid_from=2024-01-15)
(Вклад "Премьер", требуемый документ, Паспорт)
[Relevant Summary]
На 2024-02-01 действует ставка 6.0% годовых (введена 2024-01-15). Архивная ставка 5.5% действовала до 2024-01-15.

[Question #2]
Сколько действует гарантия на ноутбук MacBook Pro в России?
[Found Information #2]
(Ноутбук MacBook Pro, гарантия в России (месяцы), 12)
(Ноутбук MacBook Pro, гарантия в Европе (месяцы), 24)
(Сервисные центры, размещены на, официальный сайт)
[Relevant Summary]
Гарантия на MacBook Pro в РФ - 12 месяцев.

[Question #3]
Какова высота вершины "Орин" (в метрах)?
[Found Information #3]
(Регион Орин, сезонные рекомендации, июнь–сентябрь)
(Озеро Орин, рядом, кемпинг)
[Relevant Summary]
<|NoRelevantInfo|>
"""

RU_CAGEN_USER_PROMPT = \
    """
[Question]
{q}
[Finded Information]
{c}
"""

RU_CAGEN_ASSISTANT_PROMPT = \
    """
[Relevant Summary]
"""
