EN_REPH_CHUNK_SYSTEM_PROMPT = \
    '''
Your task is to rephrase the dialogue fragment [Dialogue] so that each utterance becomes convenient for fact extraction and knowledge graph construction.

Key goal:
Make all entities related to the user and the user's environment explicit, and eliminate ambiguous pronouns ("I", "we", "he", "she", "they", "you", etc.) by replacing them with explicit descriptions such as:
- "the user"
- "the user's brother"
- "the user's mother"
- "the user's colleagues"
and so on, whenever this clearly follows from the context.

Important:
- Do NOT add new facts or conclusions - rely only on the text of [Dialogue].
- Do NOT remove facts that may be useful for the graph (about the user, their environment, events, objects, places, time, etc.).
- Do NOT merge or split messages: for each input message there must be exactly one rephrased utterance.
- Do NOT change the order of messages.

Handling entities and pronouns:
1. User messages:
   - Replace first-person pronouns ("I", "me", "my", "we", etc.) with "the user" or a more precise expression:
     Example: "I love dogs" -> "the user loves dogs".
   - If the context makes it clear who "he/she/they" refers to, replace it with an explicit entity linked to the user:
     Example: "I have a sister, she lives in Yekaterinburg" ->
              "the user has a sister, the user's sister lives in Yekaterinburg".
   - Preserve temporal and quantitative characteristics:
     "I have two dogs and one parrot at home" ->
     "the user has two dogs and one parrot living at the user's home".

2. Assistant messages:
   - We do not need the assistant as a node in the graph. Avoid phrases like "I think", "I recommend", "as an assistant".
   - Rephrase in a way that highlights information and recommendations about the user:
     "I recommend that you get more rest" -> "it is recommended that the user get more rest".
   - If the assistant describes facts about the user or their environment, also make pronouns explicit:
     "you work a lot and get tired" -> "the user works a lot and often gets tired".

3. User's environment:
   - If there are relatives, friends, colleagues, etc., tie them to the user as explicitly as possible:
     "my brother is an engineer" -> "the user's brother works as an engineer".
     "they live with us" (about the parents) -> "the user's parents live together with the user".

Overall style:
1. Preserve the language (Russian) and the general style of the original fragment.
2. Preserve exact numbers, units of measurement, dates, proper names, and organization names.
3. Aim for clear, sufficiently complete, but not excessively "bloated" formulations.
4. You may slightly rearrange the order of words and sentences if this helps to make relations more explicit, but do not change the meaning.
5. Preserve two-line spacing between rephrased messages. Always preserve the roles in the rephrased messages and mark them with the same symbols (||user|| or ||assistant||).


Input format:
[Dialogue] - the original fragment of a dialogue between the user and the assistant.
Each message has the format: ||user||: <user message text> or ||assistant||: <assistant message text>.
Messages are in chronological order. There are exactly two empty line breaks between messages.

Output format:
[Rephrased dialogue] - rephrased messages with preservation of:
- the same number of messages,
- the same order of messages,
- the same roles (||user|| or ||assistant||),
- two empty line breaks between neighboring messages.

Very important:
1. For each input message there must be exactly one rephrased message.
2. Do not add headings, comments, or explanations.
3. Do not add any service blocks besides the messages themselves.
4. Preserve exactly TWO empty line breaks between rephrased messages.
5. The role must be at the beginning of the line in the form "||user||:" or "||assistant||:", as in the original dialogue.


Examples:
[Dialogue #1]
1. ||user||: I love dogs. I have two dogs and a parrot at home.


2. ||assistant||: That's great! Pets really help you relax.


3. ||user||: They always wait for me when I come home from work and greet me.


[Rephrased dialogue]
1. ||user||: The user loves dogs; the user has two dogs and one parrot living at the user's home.


2. ||assistant||: Pets help the user relax.


3. ||user||: The user's dogs and parrot always wait for the user to come home from work and greet the user.


[Dialogue #2]
1. ||user||: I have a sister, she lives in Yekaterinburg. She often comes to visit me.


2. ||assistant||: It's great that you have such warm communication.


3. ||user||: She is a doctor and works a lot, so we don't see each other very often.


[Rephrased dialogue]
1. ||user||: The user has a sister, the user's sister lives in Yekaterinburg; the user's sister often comes to visit the user.


2. ||assistant||: It is important that the user maintains warm and close relations with the user's sister.


3. ||user||: The user's sister works as a doctor and works a lot, so the user and the user's sister do not see each other very often.
'''

EN_REPH_CHUNK_USER_PROMPT = \
    '''
[Dialogue]
{dialogue}
'''

EN_REPH_CHUNK_ASSISTANT_PROMPT = \
    '''
[Rephrased dialogue]
'''


# == Prompts in Russian ==

RU_REPH_CHUNK_SYSTEM_PROMPT = \
    '''
Ваша задача - переформулировать фрагмент диалога [Dialogue] так, чтобы каждая реплика стала удобной для извлечения фактов и построения графа знаний.

Ключевая цель:
Сделать явными все сущности, связанные с пользователем и его окружением, а также устранить двусмысленные местоимения ("я", "мы", "он", "она", "они", "ты", "вы" и т.п.), заменив их на явные описания вида:
- "пользователь"
- "брат пользователя"
- "мама пользователя"
- "коллеги пользователя"
и т.п., если это однозначно следует из контекста.

Важно:
- НЕ добавляйте новых фактов и выводов - опирайтесь только на текст [Dialogue].
- НЕ удаляйте факты, которые могут быть полезны для графа (о пользователе, его окружении, событиях, предметах, местах, времени и т.п.).
- НЕ объединяйте и НЕ разделяйте сообщения: на каждое входное сообщение должна приходиться ровно одна переформулированная реплика.
- НЕ меняйте порядок сообщений.

Обработка сущностей и местоимений:
1. Сообщения пользователя:
   - Местоимения первого лица ("я", "мне", "меня", "мы" и т.п.) заменяйте на "пользователь" или более точное выражение:
     Пример: "я люблю кошек" -> "пользователь любит кошек".
   - Если из контекста ясно, кто такой "он/она/они", заменяйте на явную сущность, связанную с пользователем:
     Пример: "у меня есть сестра, она живёт в Екатеринбурге" -> "у пользователя есть сестра, сестра пользователя живёт в Екатеринбурге".
   - Сохраняйте временные и количественные характеристики: "у меня дома две собаки и один попугай" -> "дома у пользователя живут две собаки и один попугай".

2. Сообщения ассистента:
   - Сущность ассистента как узел графа нам не нужна. Избегайте фраз вида "я думаю", "я советую", "как ассистент".
   - Переформулируйте так, чтобы выделить информацию и рекомендации относительно пользователя:
     "Я рекомендую вам больше отдыхать" -> "пользователю рекомендуется больше отдыхать".
   - Если ассистент описывает факты о пользователе или его окружении, также делайте местоимения явными:
     "вы много работаете и устаёте" -> "пользователь много работает и часто устаёт".

3. Окружение пользователя:
   - Если есть родственники, друзья, коллеги и т.п., максимально явно привязывайте их к пользователю:
     "мой брат инженер" -> "брат пользователя работает инженером".
     "они живут с нами" (о родителях) -> "родители пользователя живут вместе с пользователем".

Общий стиль:
1. Сохраняйте язык (русский) и общий стиль исходного фрагмента.
2. Сохраняйте точные числа, единицы измерения, даты, имена собственные, названия организаций.
3. Стремитесь к ясным, достаточно полным, но не чрезмерно "раздутым" формулировкам.
4. Можно слегка перестраивать порядок слов и предложений, если это помогает сделать связи более явными, но не меняйте смысл.
5. Сохраняте отступы в 2 строки между перефразированными сообщениями. Обязательно сохраняйте роли в перефразированных сообщениях и выделяйте их теми же символами (||user|| или ||assistant||).


Формат ввода:
[Dialogue] - исходный фрагмент диалога между пользователем и ассистентом.
Каждое сообщение имеет формат: ||user||: <текст сообщения пользователя> или ||assistant||: <текст сообщения ассистента>
Сообщения идут в хронологическом порядке. Между сообщениями - два пустых переноса строки.

Формат вывода:
[Rephrased dialogue] - переформулированные сообщения с сохранением:
- того же количества сообщений,
- того же порядка сообщений,
- тех же ролей (||user|| или ||assistant||),
- двух пустых строк между соседними сообщениями.

Очень важно:
1. На каждое входное сообщение ровно одно переформулированное сообщение.
2. Не добавляйте заголовков, комментариев, пояснений.
3. Не добавляйте никаких служебных блоков, кроме самих сообщений.
4. Между перефразированными сообщениями сохраняйте ровно ДВА пустых переноса строки.
5. Роль должна быть в начале строки в виде "||user||:" или "||assistant||:" как в исходном диалоге.


Примеры:
[Dialogue #1]
1. ||user||: Я люблю собак. У меня дома две собаки и попугай.


2. ||assistant||: Здорово! Животные действительно помогают расслабиться.


3. ||user||: Они всегда ждут меня с работы и встречают.


[Rephrased dialogue]
1. ||user||: Пользователь любит собак; дома у пользователя живут две собаки и один попугай.


2. ||assistant||: Домашние животные помогают пользователю расслабиться.


3. ||user||: Собаки и попугай пользователя всегда ждут пользователя с работы и встречают его.


[Dialogue #2]
1. ||user||: У меня есть сестра, она живёт в Екатеринбурге. Она часто приезжает ко мне.


2. ||assistant||: Это здорово, что вы так тепло общаетесь.


3. ||user||: Она врач и много работает, поэтому мы видимся не так часто.


[Rephrased dialogue]
1. ||user||: У пользователя есть сестра, сестра пользователя живёт в Екатеринбурге; сестра пользователя часто приезжает к пользователю.


2. ||assistant||: Важно, что пользователь поддерживает тёплые и близкие отношения с сестрой пользователя.


3. ||user||: Сестра пользователя работает врачим и много работает, поэтому пользователь и сестра пользователя видятся не так часто.
'''

RU_REPH_CHUNK_USER_PROMPT = \
    '''
[Dialogue]
{dialogue}
'''

RU_REPH_CHUNK_ASSISTANT_PROMPT = \
    '''
[Rephrased dialogue]
'''
