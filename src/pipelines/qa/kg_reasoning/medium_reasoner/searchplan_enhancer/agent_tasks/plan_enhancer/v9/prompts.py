### PROMPT IN ENGLISH ###

EN_PLANENH_SYSTEM_PROMPT = \
    '''
Your task is, given the original question [Question], the related search plan and the information found based on it [Complited search-plan queries], to improve/reformulate the following search queries [Next search-plan queries at now] in order to find more relevant information for producing a more precise/correct answer.

Rules:
1. The search plan must be presented as a list of search queries that can potentially lead to obtaining the necessary knowledge.
2. When generating the next expanded search queries [Enhanced next search-plan queries], take into account the entire previous context of the plan.
3. The search queries must be independent in the sense that answering one query must not require knowing the contents of the other queries.
4. Every individual query of the search plan must be information-consistent and contains all required knowledge to be executed independently from the other plan queries and without internal intent/request distortion.
5. Do not use any external knowledge. Rely only on the provided information.
6. If [Next search-plan queries at now] have queries, which contains undefined/uncertain or relative key words (in squared brackets, for example), that can be clarified by the information from [Complited search-plan queries], then enhance/update/clarify them.
7. If [Next search-plan queries at now] contains query, which can not be executed independently from information in [Complited search-plan queries], then clarify/update it.
8. If answer for query from [Complited search-plan queries] did not give relevant information for [Question], then try to decompose that query on simple, single-hop ones and add them to [Enhanced next search-plan queries].
9. If additional search step in plan must be generated to prepare relevant and/or accurate answer on [Question], then generate them and add them to [Enhanced next search-plan queries].
10. If <|NoSearchSteps|> in [Next search-plan queries at now], then generate new search steps, which must be executed to get information for accurate answer generation on given [Question], and add them to [Enhanced next search-plan queries].
11. Preserve exact numbers, units of measurement, and dates.
12. Return your response in english.

Input format:
[Question] - the original question.
[Complited search-plan queries] - the completed search queries from the search plan together with the information found based on them.
[Next search-plan queries at now] - the next search queries from the search plan at the current moment.
Output format:
[Enhanced next search-plan queries] - the expanded next search queries in the following format:
1. <sub-query #1>
2. <sub-query #2>
...
N. <sub-query #N>

Examples:

[Question #1]
Who was the writer of "Stranger in Moscow" and who died in 2009?
[Complited search-plan queries #1]
Search Query: Who wrote the song "Stranger in Moscow"?
Finded information: The song "Stranger in Moscow" was written by Michael Jackson.
Search Query: Which composers died in 2009?
Finded information: Maurice jarre, Isaac Schwartz.
[Next search-plan queries at now #1]
1. Famous musicians who died in 2009 and wrote famous songs.
[Enhanced next search-plan queries #1]
1. Biography and date of death of Michael Jackson.

[Question #2]
Do both films Payment On Demand and My Cousin From Warsaw have the directors from the same country?
[Complited search-plan queries #2]
Search Query: What is the director of the film Payment On Demand?
Finded information: Curtis Bernhardt
Search Query: What is the director of the film My Cousin From Warsaw?
Finded information: Carl Boese is the director of the film My Cousin From Warsaw.
[Next search-plan queries at now #2]
1. What country is the director of Payment On Demand from?
2. What country is the director of My Cousin From Warsaw from?
[Enhanced next search-plan queries #2]
1. What country is Carl Boese from?
2. What country is Curtis Bernhardt from?

[Question #3]
What is the place of birth of the director of film And The Spring Comes?
[Complited search-plan queries #3]
Search Query: Who directed the film "And The Spring Comes"
Finded information: Gu Changwei directed the film "And The Spring Comes"
[Next search-plan queries at now #3]
1. What is the place of birth of [director's name]?
[Enhanced next search-plan queries #3]
1. What is the place of birth of Gu Changwei?

[Question #4]
What is the award that the director of film Wearing Velvet Slippers Under A Golden Umbrella won?
[Complited search-plan queries #4]
Search Query: Who directed the film "Wearing Velvet Slippers Under A Golden Umbrella"?
Finded information: Maung Wunna directed the film "Wearing Velvet Slippers Under A Golden Umbrella".
Search Query: What awards has Maung Wunna won?
Finded information: Maung Wunna has won two Myanmar Motion Picture Academy Awards.
[Next search-plan queries at now #4]
<|NoSearchSteps|>
[Enhanced next search-plan queries #4]
1. Does Maung Wunna has won "Myanmar Motion Picture Academy Award" for film "Wearing Velvet Slippers Under A Golden Umbrella"?

[Question #5]
Do both films Payment On Demand and My Cousin From Warsaw have the directors from the same country?
[Complited search-plan queries #5]
Search Query: What is the director of the film Payment On Demand?
Finded information: Curtis Bernhardt
Search Query: What is the director of the film My Cousin From Warsaw?
Finded information: Carl Boese is the director of the film My Cousin From Warsaw.
[Next search-plan queries at now #5]
<|NoSearchSteps|>
[Enhanced next search-plan queries #5]
1. What country is Carl Boese from?
2. What country is Curtis Bernhardt from?
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
3. Поисковые запросы должны быть независимы в том смысле, что для ответа на один запрос необязательно знать остальные запросы.
4. Каждый отдельный запрос в плане поиска должен быть информационно-согласованным и содержать все необходимые знания для независимого выполнения от других запросов плана и без искажения внутреннего намерения.
5. Не используйте внешние знания. Опирайтесь только на предоставленную информацию.
6. Если [Next search-plan queries at now] содержат запросы, включающие неопределенные (в квадратных скобках, например) ключевые слова или местоимения, которые можно уточнить с помощью информации из [Complited search-plan queries], то улучшите/переформулируйте их.
7. Если в [Next search-plan queries at now] содержится запрос, который не может быть выполнен независимо от информации в [Complited search-plan queries], то уточните/обновите его.
8. Если ответ на запрос из [Complited search-plan queries] не дал релевантной информации для [Question], попробуйте разложить этот запрос на простые одношаговые запросы и добавить их в [Enhanced next search-plan queries].
9. Если для подготовки релевантного и/или точного ответа на [Question] необходимо выполнить дополнительные шаги поиска, то сгенерируйте их и добавьте в [Enhanced next search-plan queries].
10. Если <|NoNextSearchSteps|> в [Next search-plan queries at now], то сгенерируйте новые шаги поиска, которые необходимо выполнить для получения информации для генерации точного ответа на заданный [Question], и добавьте их в [Enhanced next search-plan queries].
11. Сохраняйте точные числа, единицы измерения и даты.
12. Верни свой ответ на русском языке.

Формат ввода:
[Question] - исходный вопрос.
[Complited search-plan queries] - выполненные поисковые запросы из плана поиска вместе с найденной на их основе информацией.
[Next search-plan queries at now] - следующие поисковые запросы из плана поиска на данный момент.
Формат вывода:
[Enhanced next search-plan queries] - расширенные следующие поисковые запросы в следующем формате:
1. <подзапрос #1>
2. <подзапрос #2>
...
N. <подзапрос #N>

Примеры:

[Question #1]
Какой композитор был автором песни "Stranger in Moscow", кто умер в 2009 году?
[Complited search-plan queries #1]
Search Query: Кто был автором песни "Stranger in Moscow"?
Finded information: Песню "Stranger in Moscow" написал Майкл Джексон.
Search Query: Какие композиторы умерли в 2009 году?
Finded information: Морис Жарр, Исаак Шварц.
[Next search-plan queries at now #1]
1. Известные музыканты, умершие в 2009 году и написавшие знаменитые песни.
[Enhanced next search-plan queries #1]
1. Биография и дата смерти Майкла Джексона.

[Question #2]
Режиссёрами фильмов "Payment On Demand" и "My Cousin From Warsaw" являются выходцы из одной страны?
[Complited search-plan queries #2]
Search Query: Кто является режиссёром фильма "Payment On Demand"?
Finded information: Кертис Бернхардт
Search Query: Кто режиссёр фильма "My Cousin From Warsaw"?
Finded information: Карл Боэзе — режиссёр фильма "My Cousin From Warsaw".
[Next search-plan queries at now #2]
1. Из какой страны директор фильма "Payment On Demand"?
2. Из какой страны режиссер фильма "My Cousin From Warsaw"?
[Enhanced next search-plan queries #2]
1. Из какой страны родом Кертис Бернхардт?
2. Из какой страны Карл Боэзе?

[Question #3]
Где родился режиссёр фильма "And The Spring Comes"?
[Complited search-plan queries #3]
Search Query: Кто снял фильм "And The Spring Comes"?
Finded information: Режиссёром фильма "And The Spring Comes" выступил Гу Чанвэй
[Next search-plan queries at now #3]
1. Где родился [имя режиссёра]?
[Enhanced next search-plan queries #3]
1. Где родился Гу Чанвэй?

[Question #4]
Какую награду получил режиссер фильма "Wearing Velvet Slippers Under A Golden Umbrella"?
[Complited search-plan queries #4]
Search Query: Кто снял фильм "Wearing Velvet Slippers Under A Golden Umbrella"?
Finded information: Фильм "Wearing Velvet Slippers Under A Golden Umbrella" снял Маунг Вунна.
Search Query: Какие награды получил Маунг Вунна?
Finded information: Маунг Вунна получил две премии Киноакадемии Мьянмы.
[Next search-plan queries at now #4]
<|NoSearchSteps|>
[Enhanced next search-plan queries #4]
1. Получил ли Маунг Вунна премию Киноакадемии Мьянмы за фильм "Wearing Velvet Slippers Under A Golden Umbrella"?

[Question #5]
Режиссёрами фильмов "Payment On Demand" и "My Cousin From Warsaw" являются выходцы из одной страны?
[Complited search-plan queries #5]
Search Query: Кто является режиссёром фильма "Payment On Demand"?
Finded information: Кертис Бернхардт
Search Query: Кто режиссёр фильма "My Cousin From Warsaw"?
Finded information: Карл Боэзе — режиссёр фильма "My Cousin From Warsaw".
[Next search-plan queries at now #5]
<|NoSearchSteps|>
[Enhanced next search-plan queries #5]
1. Из какой страны родом Кертис Бернхардт?
2. Из какой страны Карл Боэзе?
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
