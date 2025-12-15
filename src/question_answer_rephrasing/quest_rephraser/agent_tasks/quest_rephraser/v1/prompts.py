### PROMPT IN ENGLISH ###

EN_QUEST_REPH_SYSTEM_PROMPT = \
    '''
Task: Your goal is to rewrite the question [Original question] so that it is compatible with the reformatted dialog data used to build the knowledge graph.

Key Idea:
Dialogue text is stored in a form where the user and their environment are explicitly specified. For example:
- "I love dogs" -> "The user loves dogs."
- "I have a brother, he lives in Kazan" -> "The user has a brother, the user's brother lives in Kazan."

You should rewrite questions in the same style, so that entities like "user", "user's husband", "user's daughter" are easily mapped to graph nodes.

IMPORTANT: You do NOT need to answer the question. You only need to rephrase it.

Recommendations:
1. Replace first-person pronouns ("I", "me", "my", "mine", "we", "our", etc.) with explicit expressions like "user" or more precise formulations.
2. If the question mentions relatives, friends, colleagues, etc., through pronouns, make them explicit and linked to the user.
3. If the meaning refers to user data (e.g., the user asks about themselves: "Am I married?", "Do I have children?"), rewrite the question so that it is explicitly about "the user".
4. Preserve the factual content and question type:
   - Do not change the meaning of the question.
   - Preserve the question type (yes/no or open-ended: who/what/where/when/how many, etc.).
   - Preserve all constraints, quantities, and named entities (dates, city names, companies, brands, etc.).
5. Do not invent new facts, entities, locations, or relationships. Do not add conditions not present in the original question.
6. Style and form:
   - Preserve the language (Russian) and general style of the original question.
   - It is acceptable to rearrange word order for clarity, but do not change the intent.
   - The result should be exactly one rewritten question without explanations or comments.

Input Format:
[Original question] — the user's original question.

Output Format:
[Rephrased question] — the rewritten question in which:
- pronouns referring to the user are replaced with "user" or explicit links like "user's husband",
- the factual meaning and question type are preserved.

Examples:

[Original question #1]
What pets do I have at home?

[Rephrased question]
What pets does the user have at home?


[Original question #2]
Do I work in a public school or a private one?

[Rephrased question]
Does the user work in a public school or a private one?


[Original question #3]
How old is my youngest son?

[Rephrased question]
How old is the user's youngest son?


[Original question #4]
Do I like Marvel movies?

[Rephrased question]
Does the user like Marvel movies?


[Original question #5]
Do I have a driver's license?

[Rephrased question]
Does the user have a driver's license?


[Original question #6]
Do my colleagues consider me a strict teacher?

[Rephrased question]
Do the user's colleagues consider the user a strict teacher?
'''

EN_QUEST_REPH_USER_PROMPT = \
    '''
[Original question]
{question}
'''

EN_QUEST_REPH_ASSISTANT_PROMPT = \
    '''
[Rephrased question]
'''


### PROMPT IN RUSSIAN ###

RU_QUEST_REPH_SYSTEM_PROMPT = \
    '''
Задача: Ваша цель - переписать вопрос [Original question] так, чтобы он был совместим с переформулированными диалоговыми данными, по которым строится граф знаний.

Ключевая идея:
Текст диалога хранится в виде, где пользователь и его окружение задаются явно. Например:
- "Я люблю собак" -> "Пользователь любит собак".
- "У меня есть брат, он живёт в Казани" -> "У пользователя есть брат, брат пользователя живёт в Казани".

Вы должны переписать вопросы в таком же стиле, чтобы сущности вроде "пользователь", "муж пользователя", "дочка пользователя" легко сопоставлялись с узлами графа.

ВАЖНО: Вам НЕ нужно отвечать на вопрос. Нужно только его переформулировать.

Рекомендации:
1. Заменяйте местоимения первого лица ("я", "мне", "меня", "мой", "моя", "мы", "наш" и т.п.) на явные выражения "пользователь" или более точные формулировки.
2. Если в вопросе фигурируют родственники, друзья, коллеги и т.п. через местоимения, сделайте их явными и привязанными к пользователю.
3. Если по смыслу речь идёт о данных пользователя (например, пользователь спрашивает про себя: "Я замужем?", "Есть ли у меня дети?"), переписывайте вопрос так, чтобы он явно был про "пользователя".
4. Сохранение фактического содержания и типа вопроса:
   - Не меняйте смысл вопроса.
   - Сохраняйте тип вопроса (общий/да-нет или уточняющий: кто/что/где/когда/сколько и т.д.).
   - Сохраняйте все ограничения, количества и именованные сущности (даты, названия городов, компаний, брендов и т.п.).
5. Не придумывайте новые факты, сущности, локации или отношения. Не добавляйте условий, которых нет в исходном вопросе.

6. Стиль и форма:
   - Сохраняйте язык (русский) и общий стиль исходного вопроса.
   - Допускается перестроить порядок слов для ясности, но нельзя менять намерение.
   - Результатом должен быть ровно один переписанный вопрос без пояснений и комментариев.

Формат ввода:
[Original question] - исходный вопрос пользователя.

Формат вывода:
[Rephrased question] - переписанный вопрос, в котором:
- местоимения, относящиеся к пользователю, заменены на "пользователь" или явные связи вроде "муж пользователя",
- фактический смысл и тип вопроса сохранены.

Примеры:

[Original question #1]
Какие питомцы у меня живут дома?

[Rephrased question]
Какие питомцы живут дома у пользователя?


[Original question #2]
Я работаю в государственной школе или в частной?

[Rephrased question]
Пользователь работает в государственной школе или в частной?


[Original question #3]
Сколько лет моему младшему сыну?

[Rephrased question]
Сколько лет младшему сыну пользователя?


[Original question #4]
Нравятся ли мне фильмы Marvel?

[Rephrased question]
Нравятся ли пользователю фильмы Marvel?


[Original question #5]
Есть ли у меня водительские права?

[Rephrased question]
Есть ли у пользователя водительские права?


[Original question #6]
Считают ли мои коллеги меня строгим учителем?

[Rephrased question]
Считают ли коллеги пользователя, что пользователь является строгим учителем?
'''

RU_QUEST_REPH_USER_PROMPT = \
    '''
[Original question]
{question}
'''

RU_QUEST_REPH_ASSISTANT_PROMPT = \
    '''
[Rephrased question]
'''
