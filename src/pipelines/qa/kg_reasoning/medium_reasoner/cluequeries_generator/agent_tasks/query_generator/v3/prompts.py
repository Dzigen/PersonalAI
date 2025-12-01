### PROMPT IN ENGLISH ###

EN_CQGEN_SYSTEM_PROMPT = '''
Your task is to generate one more specific question based on the original question and the matched entities.

Rules:
1. Use only the provided data. Do not use external knowledge.
2. Respect the correspondence between the entity groups:
    - The first group: entities extracted from the question.
    - The second group: the corresponding, more specific values (matching each position of the first group).
3. Formulate one refined question that makes the original question more specific by substituting values from the second group.
4. Preserve the language and style of the original question.
5. Do not add facts or attributes that are not present in the entities.
6. Return only the [Specific question] section. Do not generate anything else.

Input format:
[Base question] - the original question.
[Matched entities] - "key: value" pairs, where the key is from the first group and the value is from the second group.

Output format (single section):
[Specific question] - one specified question.

Examples:
[Base question #1]
Which device manufacturers does Maria prefer?
[Matched entities]
Maria: Maria
device manufacturers: Apple
[Specific question]
Does Maria prefer Apple as device manufacturer?

[Base question #2]
Which people have positive opinion about screen of Mi 10pro on 22.12.2018?
[Matched entities]
people: Abraham
screen: window
Mi 10pro: mi 10pro
22.12.2018: 22.12.2018
[Specific question]
Does Abraham have position opinion about window of Mi 10pro on 22.12.2018?

[Base question #3]
Which bank offices are open in Moscow on Sunday?
[Matched entities]
bank: Sberbank
city: Moscow
day of week: Sunday
[Specific question]
Are Sberbank offices open in Moscow on Sunday?
'''

EN_CQGEN_USER_PROMPT = '''
[Base question]
{query}
[Matched entities]
{matched_entities}
'''

EN_CQGEN_ASSISTANT_PROMPT = '''
[Specific question]
'''

### PROMPT IN RUSSIAN ###

RU_CQGEN_SYSTEM_PROMPT = \
    '''
Ваша задача - по исходному вопросу и по сопоставленным сущностям сгенерировать один более конкретный вопрос.

Правила:
1. Используйте только предоставленные данные. Не используйте внешние знания.
2. Учитывайте соответствие между группами сущностей:
    - Первая группа - сущности, извлечённые из вопроса.
    - Вторая группа - соответствующие им, более конкретные значения (подходящее к каждой позиции первой группы).
3. Формируйте один уточнённый вопрос, который конкретизирует исходный вопрос за счёт подстановки значений из второй группы.
4. Сохраняйте язык и стиль исходного вопроса (если исходный вопрос на русском, конкретный вопрос - на русском).
5. Не добавляйте фактов или атрибутов, которых нет в сущностях.
6. Верните только секцию [Specific question]. Ничего кроме этого не генерируйте.

Формат ввода:
[Base question] - исходный вопрос.
[Matched entities] - пары "ключ: значение", где ключ - из первой группы, значение - из второй группы.

Формат вывода (единственная секция):
[Specific question] - один конкретизированный вопрос.


Примеры:
[Base question #1]
Каких производителей устройств предпочитает Мария?
[Matched entities]
Мария: Мария
Производители устройств: Apple
[Specific question]
Предпочитает ли Мария Apple как производителя устройств?

[Base question #2]
Какие люди положительно отзываются об экране Mi 10pro по состоянию на 22.12.2018?
[Matched entities]
люди: Авраам
дисплей: экран
Mi 10pro: mi 10pro
22.12.2018: 22.12.2018
[Specific question]
Есть ли у Авраама положительное мнение об экране Mi 10pro по состоянию на 22.12.2018?

[Base question #3]
Какие отделения банка работают в Москве в воскресенье?
[Matched entities]
банк: Сбербанк
город: Москва
день недели: воскресенье
[Specific question]
Работают ли отделения Сбербанка в Москве в воскресенье?
'''

RU_CQGEN_USER_PROMPT = \
    '''
[Base question]
{query}
[Matched entities]
{matched_entities}
'''
RU_CQGEN_ASSISTANT_PROMPT = \
    '''
[Specific question]
'''
