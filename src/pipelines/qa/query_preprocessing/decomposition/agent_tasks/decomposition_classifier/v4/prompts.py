# == Prompts in English ==

EN_DC_SYSTEM_PROMPT = \
    '''
You must determine whether the given question [Base question] can be split into several (two or more) parallel/isolated simple questions.
Return True (the question can be split into parallel sub-questions) or False (the question should not/cannot be split into parallel sub-questions).

Rules:
1. Do not use any external knowledge. Rely only on the [Base question].
2. First, return a brief justification in the [Chain of thoughts] block. Then return the final answer in the [Answer] block.
3. Return True only if the question is clearly breaks into parallel sub-questions. If this must not be done (sub-questions have sequential relation, etc.), then return False.
4. If some of the sub-questions contain relative words, referring to the information, that expected to being received by the other sub-questions, then return False.
5. If you are unsure whether the question can be decomposed, return False.
6. If the given [Base question] is simple (single-hop), then return False.
7. Output only the [Chain of thoughts] and [Answer] blocks - do not generate anything else. In the [Answer] block, return only True or False.
8. Return your response in english.

Input format:
[Base question] - the original question.
Output format (two sections):
[Chain of thoughts] - 2-5 concise bullet points with a short justification of the decision on whether the question can be split into sub-questions.
[Answer] - True or False.

Examples:

[Base question #1]
Who was the author of the song "Stranger in Moscow" who died in 2009?
[Answer #1]
False

[Base question #2]
In 2002, what company merged with the top PC manufacturer from 1994?
[Answer #2]
False

[Base question #3]
Are Luciano Pavarotti and Domingo Placido opera singers?
[Answer #3]
True


[Base question #4]
What administrative territorial entity is the owner of Ciudad Deportiva located?
[Answer #4]
False

[Base question #5]
Which film has the director who died first, The Crime Doctor'S Courage or Vasantha Sena (1967 Film)?
[Answer #5]
True

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
Вы должны определить: можно ли разбить заданный вопрос [Base question] на несколько параллельных простых вопросов, которые не связанны между собой по запрашиваемой информации.
Верните True (вопрос можно разбить на параллельные/изолированные подвопросы) или False (вопрос не нужно/нельзя разбить на параллельные/изолированные подвопросы).

Правила:
1. Не используйте внешние знания. Опирайтесь только на [Base question].
2. Сначала верните краткое обоснование в блоке [Chain of thoughts]. Затем верните финальный ответ в блоке [Answer].
3. Возвращайте True только в том случае, если вопрос можно четко разделить на параллельные/изолированные подвопросы, которые не связаны между собой по запрашиваемой информации. Если этого сделать нельзя или этого делать не стоит (при разбиении нарушается смысл, становится сложнее восстановить исходный вопрос, подвопросы имеют последовательную зависимость и т.п.), то возвращайте False.
4. Если некоторые из подвопросов содержат относительные/неопределённые слова (местоимения), указывающие на информацию, которая, как ожидается, будет получена в других подвопросах, то вернуть False.
5. Если сомневаетесь, можно ли декомпозировать [Base question] - возвращайте False.
6. Если заданный [Base question] является простым (single-hop), то верните False.
7. Выводите только блоки [Chain of thoughts] и [Answer] - ничего кроме этого не генерируйте. В блоке [Answer] верните только True или False.
8. Верни свой ответ на русском языке.

Формат ввода:
[Base question] - исходный вопрос.
Формат вывода (две секции):
[Chain of thoughts] - 2-5 лаконичных пунктов с кратким обоснованием решения: можно ли разбить вопрос на подвопросы.
[Answer] - True или False.

Примеры:

[Base question #1]
Кто был автором песни "Stranger in Moscow", который умер в 2009 году?
[Chain of thoughts #1]
Данный вопрос является составным.
Во-первых, пользователь спрашивает, кто написал песню "Stranger in Moscow".
Во-вторых, он уточняет, что автор этой песни умер в 2009 году.
Этот вопрос не стоит разбивать на 2 под-вопроса, так как в этом случае второй подвопрос "Кто умер в 2009 году?" является слишком абстрактным и не может быть отвечен в изоляции от информации, полученной по первому подвопросу.
Ответ на него может добавить шум и в итоге запутать модель.
[Answer #1]
False

[Base question #2]
Являются ли Лучано Паваротти и Пласидо Доминго оперными певцами?
[Chain of thoughts #2]
Для ответа на данный вопрос нужно сначала понять, кто такой Лучано Паваротти и чем он знаменит.
Затем требуется установить личность второго человека Пласидо Доминго и выяснить, чем он известен.
В итоге вопрос явно разбивается на независимые подвопросы:
1. Кто такой Лучано Паваротти и чем он знаменит?
2. Кто такой Пласидо Доминго и чем он знаменит?
[Answer #2]
True

[Base question #3]
В какой административно-территориальной единице находится владелец Сьюдад Депортива?
[Chain of thoughts #3]
Этот вопрос является составным.
Во-первых, пользователь спрашивает о владельце "Сьюдад Депортива" (Ciudad Deportiva).
Во-вторых, пользователь спрашивает об административно-территориальной единице, в которой находится этот владелец.
Этот вопрос не следует разделять на два подвопроса, поскольку в таком случае второй подвопрос "Кто умер в 2009 году?" оказывается слишком абстрактным и не может быть отвечен в изоляции от информации, полученной по первому подвопросу.
[Answer #3]
False

[Base question #4]
Режиссер какого фильма умер раньше: «Мужество доктора Крима» (The Crime Doctor's Courage) или «Васанта Сена» (фильм 1967 года)?
[Chain of thoughts #4]
Чтобы ответить на этот вопрос, нам сначала нужно выяснить, кто был режиссером фильма "The Crime Doctor's Courage" и когда он скончался.
Затем нужно определить второго человека, режиссера фильма "Vasantha Sena" (1967 г.), и узнать, когда он скончался.
В итоге вопрос четко разделяется на независимые подвопросы:
1. Кто был режиссером фильма "The Crime Doctor's Courage" и когда он скончался?
2. Кто был режиссером фильма "Vasantha Sena" (1967 г.) и когда он скончался?
[Answer #4]
True
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
