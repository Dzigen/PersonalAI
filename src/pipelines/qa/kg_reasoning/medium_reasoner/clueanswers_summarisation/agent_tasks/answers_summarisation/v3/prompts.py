### PROMPT IN ENGLISH ###

EN_CASUMM_SYSTEM_PROMPT = \
    '''
Given the question [Question] and the related search queries and the information found based on them [Search info], you must generate an answer. Use only the provided information.
By "search queries" we mean more specific auxiliary questions, and by "information found based on them" we mean the answers to those questions.

Rules:
1. Do not use external knowledge. Rely only on [Search info].
2. First, return a brief justification in the [Chain of thoughts] block (2-5 points, essentially the selected facts/matches). Then return the final answer in the [Answer] block.
3. The answer must be generated only for the given [Question]. If some auxiliary question has no required information (<|NoRelevantInfo|>), this does NOT automatically mean that there is no information for the original [Question].
4. If the relevant information is insufficient for a confident answer, return strictly <|NotEnoughtInfo|> in the [Answer] block.
5. Preserve the language and style of the original [Question].
6. Preserve exact numbers, units of measurement, and dates.
7. Do not add assumptions or conclusions that are not in the source.
8. Output only the [Chain of thoughts] and [Answer] blocks - do not generate anything else.

Input format:
[Question] - the original question.
[Search info] - search queries related to the question and the information found based on them.

Output format (two sections):
[Chain of thoughts] - 2-5 concise points showing which facts from [Found Information] support the answer.
[Answer] - the final answer or strictly <|NotEnoughtInfo|>.


Examples:
[Question #1]
What is the base rate for the "Premier" deposit on 2024-02-01?
[Search info # 1]
[Search Query]
"Premier" deposit rate on the date 2024-02-01
[Finded Information]
From 2023-11-01 to 2024-01-14 the "Premier" deposit rate was 5.5%. Since 2024-01-15 the "Premier" deposit rate has been 6.0%.

[Search Query]
history of changes to the "Premier" rate
[Finded Information]
On 2023-11-05 the "Premier" deposit rate was set at 6%.

[Chain of thoughts]
As of 2024-02-01 the entry starting 2024-01-15 is applicable: 6.0%.
The 5.5% entry ended on 2024-01-14 and does not apply on 2024-02-01.
[Answer]
6.0%

[Question #2]
What is the height of the "Orin" peak (in meters)?
[Search info #2]
[Search Query]
height of the "Orin" peak
[Finded Information]
Experts recommend visiting the "Orin" region from June to September.

[Search Query]
locations near "Orin"
[Finded Information]
There is a campsite near "Orin" Lake.

[Chain of thoughts]
There is no fact about the height of the "Orin" peak in the provided data.
Only information about the season and nearby sites is found.
[Answer]
<|NotEnoughtInfo|>

[Question #3]
What is Scott Derrickson's nationality?
[Search info #3]
[Search Query]
Scott Derrickson nationality
[Finded Information]
Scott Derrickson was born in Colorado, USA.

[Search Query]
Christian Eriksen nationality
[Finded Information]
<|NoRelevantInfo|>

[Chain of thoughts]
The original question concerns only Scott Derrickson.
Based on the first auxiliary question and the information found for it, we can conclude that Scott Derrickson is American.
The lack of information for the second auxiliary question does not prevent answering the original question.
[Answer]
Scott Derrickson is American.
'''

EN_CASUMM_USER_PROMPT = \
    '''
[Question]
{query}
[Search info]
{search_info}
'''

EN_CASUMM_ASSISTANT_PROMPT = \
    '''
[Chain of thoughts]
'''

### PROMPT IN RUSSIAN ###

RU_CASUMM_SYSTEM_PROMPT = \
    '''
По заданным вопросу [Question] и связанным с ним поисковым запросам и найденной на их основе информации [Search info] вы должны сгенерировать ответ. Используйте только предоставленную информацию.
Под поисковыми запросами подразумеваются более конкретные вспомогательные вопросы, а найденная на их основе информация - ответы на них.

Правила:
1. Не используйте внешние знания. Опирайтесь только на [Search info].
2. Сначала верните краткое обоснование в блоке [Chain of thoughts] (2–5 пунктов, по сути - выбранные факты/сопоставления). Затем верните финальный ответ в блоке [Answer].
3. Ответ нужно сгенерировать только на заданный вопрос [Question]. Если на какой-то вспомогательный вопрос нет нужной информации (<|NoRelevantInfo|>) - это НЕ означает, что автоматически нет информации и на исходный вопрос [Question].
4. Если все же релевантной информации недостаточно для уверенного ответа именно на исходный вопрос, верните строго <|NotEnoughtInfo|> в блоке [Answer].
5. Сохраняйте язык и стиль исходного вопроса [Question].
6. Сохраняйте точные числа, единицы измерения и даты.
7. Не добавляйте домыслов и выводов, которых нет в источнике.
8. Выводите только блоки [Chain of thoughts] и [Answer] - ничего кроме этого не генерируйте.

Формат ввода:
[Question] - исходный вопрос.
[Search info] - связанные с вопросом поисковые запросы и найденная на их основе информация.

Формат вывода (две секции):
[Chain of thoughts] - 2–5 лаконичных пунктов, где вы показываете, какие факты из [Found Information] поддерживают ответ.
[Answer] - финальный ответ или строго <|NotEnoughtInfo|>.


Примеры:
[Question #1]
Какова базовая ставка по вкладу "Премьер" на 2024-02-01?
[Search info # 1]
[Search Query]
ставка вклада "Премьер" на дату 2024-02-01
[Finded Information]
С 2023-11-01 по 2024-01-14 ставка по вкладу "Премьер" составляла 5.5%. С 2024-01-15 ставка по вкладу "Премьер" составляет 6.0%.

[Search Query]
история изменений ставки "Премьер"
[Finded Information]
2023-11-05 ставка по вкладу "Премьер" была установлена на уровне 6%.

[Chain of thoughts]
На 2024-02-01 актуальна запись со стартом 2024-01-15: 6.0%.
Запись 5.5% закрыта 2024-01-14 и не действует на 2024-02-01.
[Answer]
6.0%

[Question #2]
Какова высота вершины "Орин" (в метрах)?
[Search info #2]
[Search Query]
высота вершины "Орин"
[Finded Information]
Эксперты рекомендуют посещать регоин "Орин" в период с июня по сентябрь.

[Search Query]
локации рядом с "Орин"
[Finded Information]
Рядом с озером "Орин" расположен кемпинг.

[Chain of thoughts]
В предоставленных данных нет факта о высоте вершины "Орин".
Найдены только сведения о сезоне и близлежащих объектах.
[Answer]
<|NotEnoughtInfo|>

[Question #3]
Какая национальность у Скотта Дерриксона?
[Search info #3]
[Search Query]
Национальность Скотта Дерриксона?
[Finded Information]
Скотт Дерриксона родился в Колорадо, США.

[Search Query]
Национальность Кристиана Эриксона?
[Finded Information]
<|NoRelevantInfo|>

[Chain of thoughts]
Исходный вопрос касается только Скотта Дерриксона.
На основе первого вспомогательного вопроса и найденной на него информации можно сделать вывод, что Скотт Дерриксон - американец.
Отсутствие информации на второй вспомогательный вопрос не препятствует ответу на исходный.
[Answer]
Скотт Дерриксон - американец.
'''

RU_CASUMM_USER_PROMPT = \
    '''
[Question]
{query}
[Search info]
{search_info}
'''

RU_CASUMM_ASSISTANT_PROMPT = \
    '''
[Chain of thoughts]
'''
