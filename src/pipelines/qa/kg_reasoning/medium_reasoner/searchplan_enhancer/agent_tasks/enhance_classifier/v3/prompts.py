### PROMPT IN ENGLISH ###

EN_ENHCLS_SYSTEM_PROMPT = \
    '''
Your task is, given the original question [Question], the related search plan and the information found based on it [Complited search-plan queries], to determine whether the following search queries should be improved/modified in order to find more relevant information and obtain a more accurate answer.
Return True (the next steps should be adjusted) or False (the next steps of the plan do not require changes).

Rules:
1. Do not use any external knowledge. Rely only on the provided information.
2. If [Next search-plan queries at now] have queries, which contains undefined key words, that can be clarified by the information from [Complited search-plan queries], then return 'True'.
3. First, return a brief justification in the [Chain of thoughts] block. Then return the final answer in the [Answer] block.
4. Output only the [Chain of thoughts] and [Answer] blocks - do not generate anything else. In the [Answer] block, return only True or False.

Input format:
[Question] - the original question.
[Complited search-plan queries] - the completed search queries from the search plan together with the information found based on them.
[Next search-plan queries at now] - the next search queries from the search plan at the current moment.
Output format (two sections):
[Chain of thoughts] - 2-5 concise bullet points with a short justification of the decision on whether the next search queries should be improved.
[Answer] - ONLY and STRICTLY "True" or "False". Do not add any descriptions/explanations to your True/False-answer.

Examples:

[Question #1]
Who was the writer of "Stranger in Moscow" and who died in 2009?
[Complited search-plan queries #1]
Search Query: Who wrote the song "Stranger in Moscow"?
Finded information: The song "Stranger in Moscow" was written by Michael Jackson.
Search Query: Which composers died in 2009?
Finded information: Maurice jarre, Isaac Schwartz.
[Next search-plan queries at now #1]
Famous musicians who died in 2009 and wrote famous songs.
[Answer #1]
True

[Question #2]
Bordan Tkachuk was the CEO of a company that provides what sort of products?
[Complited search-plan queries #1]
Search Query: What company did Bordan Tkachuk serve as CEO?
Finded information: ...
[Next search-plan queries at now #2]
What type of products does [company name] provide?"
[Answer #2]
True

'''

EN_ENHCLS_USER_PROMPT = \
    '''
[Question]
{query}

[Complited search-plan queries]
{complited_squeries}

[Next search-plan queries at now]
{next_squeries}
'''

EN_ENHCLS_ASSISTANT_PROMPT = \
    '''
[Chain of thoughts]
'''

### PROMPT IN RUSSIAN ###

RU_ENHCLS_SYSTEM_PROMPT = \
    '''
Ваша задача - по исходному вопросу [Question], связанному с ним плану поиска и найденной на его основе информации [Complited search-plan queries], определить, следует ли улучшить/изменить следующие поисковые запросы для поиска более релевантной информации и получения более точного ответа.
Верните True (следующие шаги стоит скорректировать) или False (следующие шаги плана не требуют изменений).

Правила:
1. Не используйте внешние знания. Опирайтесь только на предоставленную информацию.
2. Если [Next search-plan queries at now] содержат запросы, включающие неопределенные ключевые слова, которые можно уточнить с помощью информации из [Complited search-plan queries], то верните 'True'.
3. Сначала верните краткое обоснование в блоке [Chain of thoughts]. Затем верните финальный ответ в блоке [Answer].
4. Выводите только блоки [Chain of thoughts] и [Answer] - ничего кроме этого не генерируйте. В блоке [Answer] верните только True или False.

Формат ввода:
[Question] - исходный вопрос.
[Complited search-plan queries] - выполненные поисковые запросы из плана поиска вместе с найденной на их основе информацией.
[Next search-plan queries at now] - следующие поисковые запросы из плана поиска на данный момент.
Формат вывода (две секции):
[Chain of thoughts] - 2-5 лаконичных пунктов с кратким обоснованием решения: следует ли улучшить следующие поисковые запросы.
[Answer] - ТОЛЬКО и СТРОГО "True" или "False". Не добавляйте каких-либо дополнительных пояснений к своему True/False-ответу.

Примеры:
[Question]
Какой композитор был автором песни "Stranger in Moscow", кто умер в 2009 году?

[Complited search-plan queries]
Search Query: Кто был автором песни "Stranger in Moscow"?
Finded information: Песню "Stranger in Moscow" написал Майкл Джексон.

Search Query: Какие композиторы умерли в 2009 году?
Finded information: Морис Жарр, Исаак Шварц.

[Next search-plan queries at now]
Известные музыканты, умершие в 2009 году и написавшие знаменитые песни.

[Chain of thoughts]
Пользователь спрашивает, кто написал песню "Stranger in Moscow" и кто умер в 2009 году.
Первый шаг плана вместе с найденной информацией позволяет заключить, что песню написал Майкл Джексон.
Второй шаг плана и релеватная для него информация сообщают об известных музыкантах, умерших в 2009 году. Однако среди них нет Майкла Джексона.
Следующий шаг плана "Известные музыканты, умершие в 2009 году и написавшие знаменитые песни" выглядит абстрактным, нет гарантий, что ответ на него приблизит нас к ответу на исходный вопрос.
Если узнать дату смерти Майкла Джексона, то получится точно ответить на исходный вопрос, поэтому лучше изменить следующий шаг, например, на "Биография и дата смерти Майкла Джексона".
Итак, данный план требует коррекции.

[Answer]
True
'''

RU_ENHCLS_USER_PROMPT = \
    '''
[Question]
{query}

[Complited search-plan queries]
{complited_squeries}

[Next search-plan queries at now]
{next_squeries}
'''

RU_ENHCLS_ASSISTANT_PROMPT = \
    '''
[Chain of thoughts]
'''
