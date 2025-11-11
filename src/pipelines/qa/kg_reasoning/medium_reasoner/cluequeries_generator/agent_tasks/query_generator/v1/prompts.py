### PROMPT IN ENGLISH ###

EN_CQGEN_SYSTEM_PROMPT = '''
Given a question, first group of entities that was extracted from that question and the second groups of entities that was matched to the first group as more specific values your task is to generate more specific question based on it.

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
Используя заданный вопрос, первую группу сущностей, которая была извлеченная из данного вопроса и вторую группу сущностей, которая была сопоставлена (в качестве более конкретных значений) с первой группой, ваша задача — сгенерировать более конкретный вопрос.

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
