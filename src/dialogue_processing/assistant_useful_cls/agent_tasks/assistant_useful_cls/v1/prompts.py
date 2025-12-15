# == Prompts in English ==

EN_ASSIST_USE_CLS_SYSTEM_PROMPT = \
'''
You must determine whether the assistant message [Assistant message] is content-wise important for understanding and extracting factual information from the neighboring user messages [Previous user message] and [Next user message].
Return True (the assistant message should be included in the group) or False (the assistant message can be skipped without losing important facts or links).

Rules:
1. Do not use any external knowledge. Rely only on [Assistant message], [Previous user message] and [Next user message].
2. First, return a brief justification in the [Chain of thoughts] block. Then return the final answer in the [Answer] block.
3. Return True if the assistant message:
   - contains concrete facts, entities, events or relationships that clarify, specify or add important information to the user messages;
   - explains or reformulates user information in a more explicit way (e.g., clarifies who/what/when/why/how);
   - helps to connect facts from the previous and next user messages (e.g., makes an implicit link explicit).
4. Return False if the assistant message:
   - is mostly small talk, empathy, emotional support, generic phrases, or purely conversational "filler";
   - repeats user information almost verbatim without adding clarity or new factual links;
   - only proposes actions or asks generic questions that are not useful for building a knowledge graph (e.g., "How can I help you?", "Tell me more").
5. If you are unsure whether the assistant message is important for understanding and extracting facts from the user messages, return False.
6. Output only the [Chain of thoughts] and [Answer] blocks - do not generate anything else. In the [Answer] block, return only True or False.

Input format:
[Previous user message] - the previous user utterance in the group.
[Assistant message] - the candidate assistant message to classify.
[Next user message] - the next user utterance in the group (may be empty).

Output format (two sections):
[Chain of thoughts] - 2-5 concise bullet points with a short justification of the decision.
[Answer] - True or False.

Examples:

[Previous user message #1]
It's boring today. I'm far away from home and wait to go home to my puppies.

[Assistant message #1]
Puppies are such a source of joy! Tell me more about them: their breed, personality, habits.
Each one probably has its own special story and funny quirks.

[Next user message #1]
I have two puppies. One is very calm, the other is playful and loud.

[Chain of thoughts]
The previous user message already mentions that the user has puppies at home.
The assistant message mostly invites the user to talk more and contains generic emotional support.
It does not add concrete facts about the dogs itself, nor does it clarify relationships or entities.
The important factual information appears only in the next user message.
[Answer]
False


[Previous user message #2]
I have two puppies at home.

[Assistant message #2]
So, in total you live with two pets: two puppies. They are your domestic animals.

[Next user message #2]
Yes, they live with me in my one-room apartment.

[Chain of thoughts]
The previous user message contains facts about the number and type of pets.
The assistant message clearly restates and structures this information (two pets, two puppies) in a way that is convenient for extracting entities and relations.
This reformulation is useful for building a knowledge graph and does not just add generic filler.
[Answer]
True
'''

EN_ASSIST_USE_CLS_USER_PROMPT = \
'''
[Previous user message]
{prev_user_text}

[Assistant message]
{assistant_text}

[Next user message]
{next_user_text}
'''

EN_ASSIST_USE_CLS_ASSISTANT_PROMPT = \
'''
[Chain of thoughts]
'''


# == Prompts in Russian ==

RU_ASSIST_USE_CLS_SYSTEM_PROMPT = \
'''
Вы должны определить, является ли сообщение ассистента [Assistant message] содержательно важным для понимания и извлечения фактической информации из соседних пользовательских сообщений [Previous user message] и [Next user message].
Верните True (сообщение ассистента необходимо включить в группу) или False (сообщение ассистента можно пропустить без потери важных фактов или связей).

Правила:
1. Не используйте внешние знания. Опирайтесь только на [Assistant message], [Previous user message] и [Next user message].
2. Сначала верните краткое обоснование в блоке [Chain of thoughts]. Затем верните финальный ответ в блоке [Answer].
3. Возвращайте True, если сообщение ассистента:
   - содержит конкретные факты, сущности, события или отношения, которые уточняют, дополняют или делают более явной информацию из пользовательских сообщений;
   - явно разъясняет или переформулирует сведения пользователя (например, уточняет кто/что/когда/почему/как);
   - помогает связать факты из предыдущего и следующего пользовательских сообщений (например, делает явной скрытую связь между ними).
4. Возвращайте False, если сообщение ассистента:
   - в основном состоит из "small talk", эмпатии, эмоциональной поддержки, общих фраз или разговорного "шума";
   - лишь почти дословно повторяет информацию пользователя, не добавляя ясности и новых фактических связей;
   - содержит только общие предложения действий или вопросы, которые мало полезны для построения графа знаний (например, "Чем я могу помочь?", "Расскажите подробнее").
5. Если вы сомневаетесь, является ли сообщение ассистента важным для понимания и извлечения фактов из пользовательских сообщений, возвращайте False.
6. Выводите только блоки [Chain of thoughts] и [Answer] — ничего кроме этого не генерируйте. В блоке [Answer] верните только True или False.

Формат ввода:
[Previous user message] — предыдущее пользовательское сообщение в группе.
[Assistant message] — проверяемое сообщение ассистента.
[Next user message] — следующее пользовательское сообщение в группе (может отсутствовать).

Формат вывода (две секции):
[Chain of thoughts] — 2-5 лаконичных пунктов с кратким обоснованием решения.
[Answer] — True или False.

Примеры:

[Previous user message #1]
Сегодня мне немного скучно. Нахожусь в дали от дома и жду, когда пойду домой к своим щеночками.

[Assistant message #1]
Щеночки — это всегда вдохновение! Расскажите немного о них: породы, характеры, привычки.
Наверняка у каждого своя история и забавные повадки.

[Next user message #1]
У меня дома два щеночка. Один спокойный, другой - непоседа.

[Chain of thoughts]
Предыдущее сообщение пользователя уже говорит о том, что у него есть щенки.
Сообщение ассистента в основном состоит из эмоциональной поддержки и приглашения поговорить,
но не добавляет конкретных фактов о собаках и не уточняет существующие сведения.
Ключевая фактическая информация появляется только в следующем пользовательском сообщении.
[Answer]
False


[Previous user message #2]
У меня дома два щенка.

[Assistant message #2]
То есть всего у вас два домашних питомца: два щенка.

[Next user message #2]
Да, они живут со мной в однокомнатной квартире.

[Chain of thoughts]
Предыдущее сообщение пользователя задаёт факты о количестве и типе животных.
Сообщение ассистента чётко структурирует эту информацию (два питомца: два щенка), делая её удобной для извлечения сущностей и связей.
Это не просто "филлер", а полезная фактологическая переформулировка.
[Answer]
True
'''

RU_ASSIST_USE_CLS_USER_PROMPT = \
'''
[Previous user message]
{prev_user_text}

[Assistant message]
{assistant_text}

[Next user message]
{next_user_text}
'''

RU_ASSIST_USE_CLS_ASSISTANT_PROMPT = \
'''
[Chain of thoughts]
'''
