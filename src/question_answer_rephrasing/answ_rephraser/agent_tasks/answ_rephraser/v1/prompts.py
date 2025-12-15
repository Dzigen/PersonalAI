### PROMPT IN ENGLISH ###

EN_ANSW_REPH_SYSTEM_PROMPT = \
    '''
Task: Your goal is to rewrite the original answer [Original answer] based on the original question [Original question], the original answer [Original answer], and the rephrased question [Rephrased question], so that it is compatible with the rephrased question [Rephrased question].

Key Idea:
There is an original question and an original answer that responds to that question. There is also a slightly modified version of the original question. You need to rewrite the original answer so that it answers the modified question. You should rewrite the answer in the same style as the original answer, without changing its meaning.

IMPORTANT: Often, answers do not require rephrasing. They are already compatible with the rephrased question (e.g., yes/no answers; an exact fact in the answer; inability to provide an answer - "I don't have that information," etc.). In this case, you do not need to rephrase the answer. Leave it as is, changing nothing.

Recommendations:
1. Replace explicit expressions like "user" with appropriate pronouns.
2. If the original answer [Original answer] mentions relatives, friends, or colleagues explicitly linked to the user ("user's brother," "user's parents"), replace them with formulations using pronouns ("your brother," "your parents").
3. If the original answer [Original answer] is a concrete fact without any link to the user's personality, their environment, etc., do not change this answer.
4. Preserve the factual content and type of the original answer [Original answer]:
   - Do not change the meaning of the answer.
   - Preserve the answer type (general/yes-no or clarifying: who/what/where/when/how many, etc.).
5. Do not invent new facts, entities, locations, or relationships. Do not add information not present in the original answer [Original answer].
6. Style and form:
   - Preserve the language and general style of the original answer.
   - The result should be exactly one rewritten answer without explanations or comments.
7. The rewritten answer [Rephrased answer] must correspond to the rephrased question [Rephrased question].
8. A period must be placed at the end of the rewritten answer [Rephrased answer].
9. In most cases, rewriting the answer is not required; it already corresponds to the rephrased question [Rephrased question]. In such cases, simply return the original answer [Original answer], changing nothing.

Input Format:
[Original question] - original question.
[Original answer] - original answer.
[Rephrased question] - rephrased question.

Output Format:
[Rephrased answer] - rewritten answer.

Examples:

[Original question #1]
Do the user's parents have a car?

[Original answer #1]
The user's parents do not have a car.

[Rephrased question #1]
Do my parents have a car?

[Rephrased answer]
Your parents do not have a car.


[Original question #2]
Does the user work in the police or the National Guard?

[Original answer #2]
I don't have that information.

[Rephrased question #2]
Do I work in the police or the National Guard?

[Rephrased answer]
I don't have that information.


[Original question #3]
What kind of music does the user like?

[Original answer #3]
The user likes classical music.

[Rephrased question #3]
What kind of music do I like?

[Rephrased answer]
You like classical music.


[Original question #4]
Does the user like Marvel movies?

[Original answer #4]
No.

[Rephrased question #4]
Do I like Marvel movies?

[Rephrased answer]
No.


[Original question #5]
Is the user tall or short?

[Original answer #5]
The user is tall.

[Rephrased question #5]
Am I tall or short?

[Rephrased answer]
You are tall.


[Original question #6]
What did the user's sister's husband give the user for New Year?

[Original answer #6]
The user's sister's husband gave the user a gift certificate to "Golden Apple".

[Rephrased question #6]
What did my sister's husband give me for New Year?

[Rephrased answer]
Your sister's husband gave you a gift certificate to "Golden Apple".


[Original question #7]
Is the user older or younger than the user's best friend?

[Original answer #7]
Older.

[Rephrased question #7]
Am I older or younger than my best friend?

[Rephrased answer]
Older.


[Original question #8]
What sections did the user attend?

[Original answer #8]
The user attended boxing and swimming sections.

[Rephrased question #8]
What sections did I attend?

[Rephrased answer]
You attended boxing and swimming sections.
'''

EN_ANSW_REPH_USER_PROMPT = \
    '''
[Original question]
{rephrased_question}

[Original answer]
{raw_answer}

[Rephrased question]
{question}
'''

EN_ANSW_REPH_ASSISTANT_PROMPT = \
    '''
[Rephrased answer]
'''


### PROMPT IN RUSSIAN ###

RU_ANSW_REPH_SYSTEM_PROMPT = \
    '''
Задача: Ваша цель - по исходным вопросу [Original question] и ответу [Original answer], а также перефразированному вопросу [Rephrased question], переписать исходный ответ [Original answer] так,
чтобы он был совместим с перефразированным вопросом [Rephrased question].

Ключевая идея:
Есть исходный вопрос и исходный ответ, который отвечает на этот вопрос. Есть также немного измененный исходный вопрос. Нужно переписать исходный ответ так, чтобы он отвечал на измененный вопрос.
Вы должны переписать ответ в том же стиле, что и исходный ответ, не меняя смысл.

ВАЖНО: Зачастую ответы не требуют переформулировки. Они и так совместимы с исходным вопросом (например, ответы да/нет; точный факт в ответе; невозможность предоставить ответ - "У меня нет такой информации." и так далее).
В этом случае вам не нужно переформулировать ответ. Оставьте его как есть, ничего не меняя.

Рекомендации:
1. Заменяйте явные выражения "пользователь" на соответствующие местоимения.
2. Если в ответе [Original answer] фигурируют родственники, друзья, коллеги, явно привязынные к пользователю ("брат пользователя", "родители пользователя"), заменяйте их на формулировки с местоимениями ("ваш брат", "ваши родители").
3. Если ответ [Original answer] представляет собой конкретный факт, без привязки к личности пользователя, его окружению и тд, не меняйте этот ответ.
4. Сохранение фактического содержания и типа ответа [Original answer]:
   - Не меняйте смысл ответа.
   - Сохраняйте тип ответа (общий/да-нет или уточняющий: кто/что/где/когда/сколько и т.д.).
5. Не придумывайте новые факты, сущности, локации или отношения. Не добавляйте информации, которой нет в исходном ответе [Original answer].
6. Стиль и форма:
   - Сохраняйте язык и общий стиль исходного ответа.
   - Результатом должен быть ровно один переписанный ответ без пояснений и комментариев.
7. Переписанный ответ [Rephrased answer] должен соответствовать переформулированному вопросу [Rephrased question].
8. В конце переписанного ответа [Rephrased answer] обязательно должна стоять точка.
9. В большинстве случаев переписывать ответ не требуется, он и так соответствует переформулированному вопросу [Rephrased question]. В этом случае просто возвращайте исходный ответ [Original answer], ничего в нем не меняя.

Формат ввода:
[Original question] - исходный вопрос.
[Original answer] - исходный ответ.
[Rephrased question] - перефразированный вопрос.

Формат вывода:
[Rephrased answer] - переписанный ответ.


Примеры:

[Original question #1]
У родителей пользователя есть машина?

[Original answer #1]
У родителей пользователя нет машины.

[Rephrased question #1]
У моих родителей есть машина?

[Rephrased answer]
У ваших родителей нет машины.


[Original question #2]
Пользователь работает в полиции или росгвардии?

[Original answer #2]
У меня нет такой информации

[Rephrased question #2]
Я работаю в полиции или росгвардии?

[Rephrased answer]
У меня нет такой информации.


[Original question #3]
Какая музыка нравится пользователю?

[Original answer #3]
Пользователю нравится классическая музыка

[Rephrased question #3]
Какая музыка мне нравится?

[Rephrased answer]
Вам нравится классическая музыка.


[Original question #4]
Нравятся ли пользователю фильмы Marvel?

[Original answer #4]
Нет.

[Rephrased question #4]
Нравятся ли мне фильмы Marvel?

[Rephrased answer]
Нет.


[Original question #5]
Пользователь высокий или низкий?

[Original answer #5]
Пользователь высокий.

[Rephrased question #5]
Я высокий или низкий?

[Rephrased answer]
Вы высокий.


[Original question #6]
Что подарил муж сестры пользователя на новый год пользователю?

[Original answer #6]
Муж сестры пользователя подарил пользователю сертификат в "Золотое Яблоко".

[Rephrased question #6]
Что подарил мне муж сестры на новый год?

[Rephrased answer]
Муж сестры подарил вам сертификат в "Золотое Яблоко".


[Original question #7]
Пользователь старше или младше лучшего друга пользователя?

[Original answer #7]
Старше.

[Rephrased question #7]
Я старше или младше своего лучшего друга?

[Rephrased answer]
Старше.


[Original question #8]
Какие секции пользователь посещал?

[Original answer #8]
Пользователь посещал секции по боксу и по плаванию.

[Rephrased question #8]
Какие секции я посещал?

[Rephrased answer]
Вы посещали секции по боксу и по плаванию.
'''

RU_ANSW_REPH_USER_PROMPT = \
    '''
[Original question]
{rephrased_question}

[Original answer]
{raw_answer}

[Rephrased question]
{question}
'''

RU_ANSW_REPH_ASSISTANT_PROMPT = \
    '''
[Rephrased answer]
'''
