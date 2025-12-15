### PROMPT IN ENGLISH ###

EN_FACT_PRESRVE_SYSTEM_PROMPT = \
    '''Task: Your primary goal is to make the message [Target Message] from the dialogue shorter while preserving all factual information, entities, and the relationships between them.

Guidelines for fact-preserving summarization:

1. Preserving facts:
   - Do not remove entities (people, objects, organizations, locations, events) and important attributes (dates, quantities, conditions, causes, effects).
   - Do not remove relationships between entities (who did what, with whom, when, why, how).

2. No new information:
   - Do not invent facts not present in the source text—rely only on the text from [Target Message], [Prev Message], [Next Message].
   - Do not turn assumptions or probabilities into confident statements.
   - If something is expressed as a hypothesis, probability, or opinion, preserve that form.

3. Compression and style:
   - You can shorten the text by: removing stylistic repetitions, simplifying long phrases, merging similar sentences, removing purely rhetorical inserts.
   - Do not change the speaker's point of view or intent.
   - The text must remain coherent and readable.

4. Pronouns and references:
   - Where possible, clarify pronouns ("he," "she," "they," "it," etc.) by explicitly indicating who or what is being referred to, using the provided context.
   - If the reference remains unclear even with context, keep the pronoun, but do not invent details.

5. Dialogue context:
   - You can use the previous [Prev Message] and next [Next Message] from the dialogue only to better understand who/what is being discussed and to clarify meaning.
   - Do not separately summarize the context; the result should be a rewritten version of the target message [Target Message], not the entire dialogue.

Input format:
[Prev Message] - the previous message (before the target)
[Target Message] - the target message for which fact-preserving summarization needs to be performed.
[Next Message] - the next message (after the target)

Output format:
[Summarizied Message] - the summarized message. Do not add any explanations, comments, lists, or auxiliary information around it.

Examples:

[Prev Message #1]
Tell me briefly about the AI Summit 2024 conference.

[Target Message #1]
The AI Summit 2024 conference is one of the largest events in the field of artificial intelligence in Europe, more precisely in Eastern Europe. It will take place in Warsaw, and its dates are from October 15 to October 17, 2024. The organizer, as in previous years, is the "TechFuture" foundation, and more than 5,000 participants from around the world are expected, including leading researchers from companies like DeepMind and OpenAI. The key topics to be discussed are, of course, large language models, AI ethics, and autonomous systems.

[Next Message #1]
Thanks! Who are the speakers?

[Summarizied Message]
AI Summit 2024, the largest AI conference in Eastern Europe, will take place in Warsaw from October 15 to 17. It is organized by the "TechFuture" foundation, with over 5,000 participants expected, including researchers from DeepMind and OpenAI. Key topics: large language models, AI ethics, and autonomous systems.

[Prev Message #2]
Based on your preferences, I can recommend two hotels in Rome: "The View" and "Imperial Gardens".

[Target Message #2]
Thanks! Regarding the first one, "The View," could you please clarify—is it close to the historical center, and does it have, in fact, airport transfer? This is very important to me. It's important for me to be as close to the center as possible, so as to visit most of the sights without much difficulty.

[Next Message #2]
Hotel "The View" is located within a 15-minute walk from the Colosseum and provides a paid transfer from Fiumicino Airport.

[Summarizied Message]
Please clarify if Hotel "The View" is close to the historical center and if it has airport transfer. This is very important to me. I want to be closer to the center to see more sights.
'''

EN_FACT_PRESRVE_USER_PROMPT = \
    '''
[Prev Message]
{prev_context}

[Target Message]
{text}

[Next Message]
{next_context}
'''
EN_FACT_PRESRVE_ASSISTANT_PROMPT = \
    '''
[Summarizied Message]
'''

### PROMPT IN RUSSIAN ###

RU_FACT_PRESRVE_SYSTEM_PROMPT = \
    '''Задача: Ваша основная цель — сделать сообщение [Target Message] из диалога короче, сохранив при этом все фактические сведения, сущности и связи между ними.

Рекомендации по факт-сохраняющей суммаризации:

1. Сохранение фактов:
   - Не удаляйте сущности (людей, объекты, организации, локации, события) и важные атрибуты (даты, количества, условия, причины, следствия).
   - Не удаляйте связи между сущностями (кто что сделал, с кем, когда, почему, как).

2. Без новых сведений:
   - Не выдумывайте факты, которых нет в исходном тексте - опирайтесь только на текст из [Target Message], [Prev Message], [Next Message].
   - Не превращайте предположения или вероятности в уверенные утверждения.
   - Если что-то выражено как гипотеза, вероятность или мнение, сохраните эту форму.

3. Сжатие и стиль:
   - Вы можете сокращать текст за счёт: удаления стилистических повторов, упрощения длинных фраз, объединения похожих предложений, удаления чисто риторических вставок.
   - Не меняйте точку зрения и намерения говорящего.
   - Текст должен оставаться связным и читаемым.

4. Местоимения и ссылки:
   - По возможности, раскрывайте местоимения ("он", "она", "они", "это" и т.п.), явно указывая, о ком или о чём идёт речь, используя предоставленный контекст.
   - Если даже с учётом контекста ссылка остаётся неясной, сохраните местоимение, но не придумывай детали.

5. Контекст диалога:
   - Вы можете использовать предыдущее [Prev Message] и следующее [Next Message] сообщения диалога только для того, чтобы лучше понять, о ком/о чём идёт речь и прояснить смысл.
   - Не нужно отдельно суммаризировать контекст; результатом должна быть переписанная версия целевого сообщения [Target Message], а не всего диалога.

Формат ввода:
[Prev Message] - предыдущее сообщение (перед целевым)
[Target Message] - целевое сообщение, для которого нужно выполнить факт-сохраняющую суммаризацию.
[Next Message] - следующее сообщение (после целевого)

Формат вывода:
[Summarizied Message] - суммаризованное сообщение. Не добавляй пояснений, комментариев, списков или служебной информации вокруг него.


Примеры:
[Prev Message #1]
Расскажи кратко о конференции AI Summit 2024.

[Target Message #1]
Конференция AI Summit 2024 является одним из крупнейших мероприятий в области искусственного интеллекта в Европе, если точнее, то в Восточной Европе, состоится в Варшаве, и дата её проведения — с 15 по 17 октября 2024 года.
Организатором, как и в прошлые годы, выступает фонд "TechFuture", и ожидается более 5000 участников со всего мира, включая ведущих исследователей из компаний вроде DeepMind и OpenAI. Ключевые темы, которые будут обсуждаться, — это, конечно, большие языковые модели, этика ИИ и автономные системы.

[Next Message #1]
Спасибо! А кто будет из спикеров?


[Summarizied Message]
AI Summit 2024, крупнейшая в Восточной Европе конференция по ИИ, пройдёт в Варшаве с 15 по 17 октября. Её организует фонд "TechFuture", ожидается более 5000 участников, включая исследователей из DeepMind и OpenAI.
Ключевые темы: большие языковые модели, этика ИИ и автономные системы.


[Prev Message #2]
На основе ваших предпочтений я могу порекомендовать два отеля в Риме: "The View" и "Imperial Gardens".

[Target Message #2]
Спасибо! А насчёт первого, того, который "The View", вы не могли бы пожалуйста уточнить — он находится близко к историческому центру, и есть ли в нём, собственно, трансфер от аэропорта?
Это для меня очень важно. Для меня важно быть по возможности ближе к центру, чтоб без большого труда посетить большинство достопримечательностей.

[Next Message #2]
Отель "The View" расположен в 15 минутах ходьбы от Колизея и предоставляет платный трансфер из аэропорта Фьюмичино.


[Summarizied Message]
Уточните, находится ли отель "The View" близко к историческому центру и есть ли в нём трансфер от аэропорта. Для меня это очень важно. Я хочу быть ближе к центру, чтобы посмотреть больше достопримечательностей.
'''

RU_FACT_PRESRVE_USER_PROMPT = \
    '''
[Prev Message]
{prev_context}

[Target Message]
{text}

[Next Message]
{next_context}
'''

RU_FACT_PRESRVE_ASSISTANT_PROMPT = \
    '''
[Summarizied Message]
'''
