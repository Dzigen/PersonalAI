# == Prompts in English ==

EN_DC_SYSTEM_PROMPT = \
    '''
You must determine whether the given question [Base question] can be split into several independent simple questions that can be answered separately from each other.
Return True (the question can be split into independent sub-questions) or False (the question should not/cannot be split into independent sub-questions).

Rules:
1. Do not use any external knowledge. Rely only on the [Base question].
2. First, return a brief justification in the [Chain of thoughts] block. Then return the final answer in the [Answer] block.
3. Return True only if the question is clearly decomposable into independent sub-questions. If this cannot or should not be done (the meaning is distorted by splitting / it becomes harder to reconstruct the original question, and so on), then return False.
4. If you are unsure whether the question can be decomposed, return False.
5. Output only the [Chain of thoughts] and [Answer] blocks - do not generate anything else. In the [Answer] block, return only True or False.

Input format:
[Base question] - the original question.

Output format (two sections):
[Chain of thoughts] - 2-5 concise bullet points with a short justification of the decision on whether the question can be split into sub-questions.
[Answer] - True or False.

Examples:
[Base question #1]
Are Giuseppe Verdi and Ambroise Thomas opera composers?

[Chain of thoughts]
To answer this question, we first need to understand who Giuseppe Verdi is and what he is known for.
Then we need to identify the second person, Ambroise Thomas, and find out what he is known for.
As a result, the question is clearly decomposed into independent sub-questions:
1. Who is Giuseppe Verdi and what is he known for?
2. Who is Ambroise Thomas and what is he known for?
[Answer]
True

[Base question #2]
Who was the author of the song "These Boots Are Made for Walkin'" who died in 2007?

[Chain of thoughts]
This question is a composite one.
First, the user asks who wrote the song "These Boots Are Made for Walkin'".
Second, they specify that the author of this song died in 2007.
This question should not be split into 2 sub-questions, because in that case the second sub-question, "Who died in 2007?", is too abstract.
The answer to it may introduce noise and ultimately confuse the model.
[Answer]
False

'''

EN_DC_USER_PROMPT = \
    '''
[Base question]
{query}
'''
EN_DC_ASSISTANT_PROMPT = \
    '''
[Chain of thoughts]
'''

# == Prompts in Russian ==

RU_DC_SYSTEM_PROMPT = \
    '''
Вы должны определить: можно ли разбить заданный вопрос [Base question] на несколько независимых простых вопросов, на которые можно ответить независимо друг от друга.
Верните True (вопрос можно разбить на независимые подвопросы) или False (вопрос не нужно/нельзя разбить на независимые подвопросы).

Правила:
1. Не используйте внешние знания. Опирайтесь только на [Base question].
2. Сначала верните краткое обоснование в блоке [Chain of thoughts]. Затем верните финальный ответ в блоке [Answer].
3. Возвращайте True, только если вопрос явно разделяется на независимые подвопросы. Если этого сделать нельзя или этого делать не стоит (при разбиении нарушается смысл/становится сложнее восстановить исходный вопрос и так далее), то возвращайте False.
4. Если сомневаетесь, можно ли декомпозировать вопрос - возвращайте False.
5. Выводите только блоки [Chain of thoughts] и [Answer] - ничего кроме этого не генерируйте. В блоке [Answer] верните только True или False.

Формат ввода:
[Base question] - исходный вопрос.

Формат вывода (две секции):
[Chain of thoughts] - 2-5 лаконичных пунктов с кратким обоснованием решения: можно ли разбить вопрос на подвопросы.
[Answer] - True или False.

Примеры:
[Base question #1]
Являются ли Джузеппе Верди и Амбруаз Тома оперными композиторами?

[Chain of thoughts]
Для ответа на данный вопрос нужно сначала понять, кто такой Джузеппе Верди и чем он знаменит.
Затем требуется установить личность второго человека Амбруаза Тома и выяснить, чем он известен.
В итоге вопрос явно разбивается на независимые подвопросы:
1. Кто такой Джузеппе Верди и чем он знаменит?
2. Кто такой Амбруаз Тома и чем он знаменит?
[Answer]
True

[Base question #2]
Кто был автором песни "These Boots Are Made for Walkin'", который умер в 2007 году?

[Chain of thoughts]
Данный вопрос является составным.
Во-первых, пользователь спрашивает, кто написал песню "These Boots Are Made for Walkin'".
Во-вторых, он уточняет, что автор этой песни умер в 2007 году.
Этот вопрос не стоит разбивать на 2 под-вопроса, так как в этом случае второй подвопрос "Кто умер в 2007 году?" является слишком абстрактным.
Ответ на него может добавить шум и в итоге запутать модель.
[Answer]
False
'''

RU_DC_USER_PROMPT = \
    '''
[Base question]
{query}
'''

RU_DC_ASSISTANT_PROMPT = \
    '''
[Chain of thoughts]
'''
