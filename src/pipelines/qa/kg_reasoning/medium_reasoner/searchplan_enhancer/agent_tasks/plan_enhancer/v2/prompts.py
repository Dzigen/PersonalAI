### PROMPT IN ENGLISH ###

EN_PLANENH_SYSTEM_PROMPT = \
    '''
Your task is, given the original question [Question], the related search plan and the information found based on it [Complited search-plan queries], to improve/reformulate the following search queries [Next search-plan queries at now] in order to find more relevant information for producing a more precise/correct answer.

Rules:
1. The search plan must be presented as a list of search queries that can potentially lead to obtaining the necessary knowledge.
2. When generating the next expanded search queries [Enhanced next search-plan queries], take into account the entire previous context of the plan.
3. Do not use any external knowledge. Rely only on the provided information.
4. Preserve the language and style of the original data.
5. Preserve exact numbers, units of measurement, and dates.

Input format:
[Question] - the original question.
[Complited search-plan queries] - the completed search queries from the search plan together with the information found based on them.
[Next search-plan queries at now] - the next search queries from the search plan at the current moment.

Output format:
[Enhanced next search-plan queries]] - the expanded next search queries in the following format:
1. <sub-query #1>
2. <sub-query #2>
...
N. <sub-query #N>

Example:
[Question]
Who was the writer of "Stranger in Moscow" and who died in 2009?

[Complited search-plan queries]
Search Query: Who wrote the song "Stranger in Moscow"?
Finded information: The song "Stranger in Moscow" was written by Michael Jackson.

Search Query: Which composers died in 2009?
Finded information: Maurice jarre, Isaac Schwartz.

[Next search-plan queries at now]
Famous musicians who died in 2009 and wrote famous songs.

[Enhanced next search-plan queries]
1. Biography and date of death of Michael Jackson.
'''

EN_PLANENH_USER_PROMPT = \
    '''
[Question]
{query}

[Complited search-plan queries]
{complited_squeries}

[Next search-plan queries at now]
{next_squeries}
'''

EN_PLANENH_ASSISTANT_PROMPT = \
    '''
[Enhanced next search-plan queries]
'''

### PROMPT IN RUSSIAN ###

RU_PLANENH_SYSTEM_PROMPT = \
    '''
Ваша задача - по исходному вопросу [Question], связанному с ним плану поиска и найденной на его основе информации [Complited search-plan queries], улучшить/переформулировать следующие поисковые запросы [Next search-plan queries at now], чтобы найти более релевантную информацию для получения более точного/корректного ответа.

Правила:
1. План поиска должен быть представлен в виде списка поисковых запросов, которые потенциально могут привести к получению необходимых знаний.
2. При генерации следующих расширенных поисковых запросов [Enhanced next search-plan queries] учитывайте весь предыдущий контекст плана.
3. Не используйте внешние знания. Опирайтесь только на предоставленную информацию.
4. Сохраняйте язык и стиль исходных данных.
5. Сохраняйте точные числа, единицы измерения и даты.

Формат ввода:
[Question] - исходный вопрос.
[Complited search-plan queries] - выполненные поисковые запросы из плана поиска вместе с найденной на их основе информацией.
[Next search-plan queries at now] - следующие поисковые запросы из плана поиска на данный момент.

Формат вывода:
[Enhanced next search-plan queries]] - расширенные следующие поисковые запросы в следующем формате:
1. <подзапрос #1>
2. <подзапрос #2>
...
N. <подзапрос #N>

Пример:
[Question]
Какой композитор был автором песни "Stranger in Moscow", кто умер в 2009 году?

[Complited search-plan queries]
Search Query: Кто был автором песни "Stranger in Moscow"?
Finded information: Песню "Stranger in Moscow" написал Майкл Джексон.

Search Query: Какие композиторы умерли в 2009 году?
Finded information: Морис Жарр, Исаак Шварц.

[Next search-plan queries at now]
Известные музыканты, умершие в 2009 году и написавшие знаменитые песни.

[Enhanced next search-plan queries]
1. Биография и дата смерти Майкла Джексона.
'''

RU_PLANENH_USER_PROMPT = \
    '''
[Question]
{query}

[Complited search-plan queries]
{complited_squeries}

[Next search-plan queries at now]
{next_squeries}
'''

RU_PLANENH_ASSISTANT_PROMPT = \
    '''
[Enhanced next search-plan queries]
'''
