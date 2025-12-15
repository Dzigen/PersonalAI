# == Prompts for User Message Grouping by Context (English) ==

EN_SAME_CTX_CLS_SYSTEM_PROMPT = \
    '''
You must determine whether the current user message [Current message] continues the same context/topic as the previous user message [Previous message], or it starts a new, separate context/topic.
Return True (the current message continues the same context) or False (the current message starts a new context).

Rules:
1. Do not use any external knowledge. Rely only on [Previous message] and [Current message].
2. First, return a brief justification in the [Chain of thoughts] block. Then return the final answer in the [Answer] block.
3. Return True only if the current message is clearly a continuation of the same topic/context:
   - it clarifies, specifies or develops the same situation, object, problem, story or question;
   - it refers to the same entities, events or issues (possibly using pronouns or ellipsis);
   - it can naturally be interpreted as the next step of the same conversation line.
4. Return False if:
   - the current message switches to a different topic (new problem, new story, new task, new addressee);
   - the connection is only stylistic (e.g., similar tone) but the subject or goal changes.
5. If you are unsure whether the current message continues the same context, return False.
6. Output only the [Chain of thoughts] and [Answer] blocks – do not generate anything else. In the [Answer] block, return only True or False.

Input format:
[Previous message] – the last user message in the current group.
[Current message] – the next user message that must be classified as "same context" or "new context".

Output format (two sections):
[Chain of thoughts] – 2–5 concise bullet points with a short justification of the decision.
[Answer] – True or False.

Examples:
[Previous message #1]
It's unbearably hot at home, and my fan can't cope anymore.

[Current message #1]
By the way, I also read an article about whether it's harmful to sleep under a fan. Is this really dangerous for health?

[Chain of thoughts]
Both messages are about heat and using a fan.
In the first message, the user complains about the heat and the fan not being enough.
In the second message, the user asks for clarification related to the safety of using a fan while sleeping.
The second message deepens the same topic (fan usage and heat), rather than switching to a new one.
[Answer]
True

[Previous message #2]
It's unbearably hot at home, and my fan can't cope anymore.

[Current message #2]
And by the way, can you recommend some good books on personal finance?

[Chain of thoughts]
The previous message is about heat and the fan at home.
The current message asks about book recommendations on personal finance, which is a completely different topic.
There is no meaningful topical continuity between the two messages.
[Answer]
False
'''

EN_SAME_CTX_CLS_USER_PROMPT = \
    '''
[Previous message]
{prev_user_text}

[Current message]
{curr_text}
'''

EN_SAME_CTX_CLS_ASSISTANT_PROMPT = \
    '''
[Chain of thoughts]
'''


# == Prompts for User Message Grouping by Context (Russian) ==

RU_SAME_CTX_CLS_SYSTEM_PROMPT = \
    '''
Вы должны определить, является ли текущее пользовательское сообщение [Current message] продолжением того же контекста/темы, что и предыдущее пользовательское сообщение [Previous message], или же оно начинает новый, отдельный контекст/тему.
Верните True (текущее сообщение продолжает тот же контекст) или False (текущее сообщение начинает новый контекст).

Правила:
1. Не используйте внешние знания. Опирайтесь только на [Previous message] и [Current message].
2. Сначала верните краткое обоснование в блоке [Chain of thoughts]. Затем верните финальный ответ в блоке [Answer].
3. Возвращайте True только в том случае, если текущее сообщение явно продолжает ту же тему/контекст:
   - оно уточняет, развивает или дополняет ту же ситуацию, объект, проблему, историю или вопрос;
   - оно ссылается на те же сущности, события или вопросы (в том числе через местоимения или опущенные детали);
   - его естественно воспринимать как следующий шаг в той же линии разговора.
4. Возвращайте False, если:
   - текущее сообщение переключается на другую тему (новая проблема, новая история, новая задача, другой адресат);
   - связь только стилистическая (например, похожий тон), но предмет разговора или цель меняются.
5. Если вы сомневаетесь, является ли текущее сообщение продолжением того же контекста, возвращайте False.
6. Выводите только блоки [Chain of thoughts] и [Answer] — ничего кроме этого не генерируйте. В блоке [Answer] верните только True или False.

Формат ввода:
[Previous message] — последнее пользовательское сообщение в текущей группе.
[Current message] — следующее пользовательское сообщение, которое нужно отнести к "тому же контексту" или к "новому контексту".

Формат вывода (две секции):
[Chain of thoughts] — 2–5 лаконичных пунктов с кратким обоснованием решения.
[Answer] — True или False.

Примеры:
[Previous message #1]
Какая же духота дома, у меня вентилятор вообще не справляется.

[Current message #1]
Кстати, я ещё прочитала статью про то, вредно ли спать под вентилятором. Это действительно опасно для здоровья?

[Chain of thoughts]
Оба сообщения связаны с жарой и использованием вентилятора.
В первом сообщении пользователь жалуется на жару и слабый эффект вентилятора.
Во втором сообщении он уточняет вопрос, связанный с безопасностью сна под вентилятором.
Второе сообщение углубляет ту же тему (использование вентилятора и жара), а не вводит новую.
[Answer]
True

[Previous message #2]
Какая же духота дома, у меня вентилятор вообще не справляется.

[Current message #2]
И ещё, порекомендуй, пожалуйста, хорошие книги по личным финансам.

[Chain of thoughts]
Предыдущее сообщение посвящено жаре и вентилятору.
Текущее сообщение спрашивает про книги по личным финансам, что является совершенно другой темой.
Между сообщениями нет содержательной тематической продолженности.
[Answer]
False
'''

RU_SAME_CTX_CLS_USER_PROMPT = \
    '''
[Previous message]
{prev_user_text}

[Current message]
{curr_text}
'''

RU_SAME_CTX_CLS_ASSISTANT_PROMPT = \
    '''
[Chain of thoughts]
'''
