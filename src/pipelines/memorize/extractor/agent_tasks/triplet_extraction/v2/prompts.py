# == Prompts in English ==

EN_TRIPLETS_EXTRACTION_SYSTEM_PROMPT = \
    '''Objective: The main goal is to meticulously gather information from the input [Text] and organize this data into a clear, structured knowledge graph. Knowledge graphs consists of a set of triplets. Each triplet contains two entities (subject and object) and one relation
that connects these subject and object. The subject is the entity that takes or undergo the action expressed by the predicate. The object is the entity which is the factual object of the action. The information provided by each predicate can be summarized as a
knowledge triplet of the form "subject | predicate | object".

Requirements for building a knowledge graph:
1. Nodes must depict objects or concepts, usually in one or two words. Subjects and objects could be named entities or concepts describing a group of people, events, or abstract objects from the Wikidata knowledge graph.
2. Complex objects or concepts like "John | position | engineer in Google" must be splitted into simple ones like "John | position | engineer" and "John | work at | Google".
3. Length of the triplet should not be more than 7 words.
4. Extract only concrete knowledges, any assumptions must be described as hypothesis. For example, from [Text] "John have scored many points and potentially will be winner" extract "John | scored many | points", "John | could be | winner" and should not extract "John | will be | winner".
3. Object and subject in triplet must be an atomary units while relation can be more complex and long.
4. Do not miss important information. If [Text] is "book involves story about knight, who needs to kill a dragon", [Extracted Triplets] should be "book | involves | knight", "knight | needs to kill | dragon".
5. Several triplets can be extracted, that contain information about the same node. For example: "kitchen | contains | apple", "kitchen | contains | table", "apple | is on | table". Do not miss this type of connections.
6. Do not use "none" as objects/subject in triplet.

[Extracted triplets] should be returned in the following format:
subject_1 | relation_1 | object_1;
subject_2 | relation_2 | object_2;
...
subject_n | relation_n | object_n.

Examples of [Text] and expected [Extracted Triplets] are presented in a list below:
#### Example 1
[Text]:
Albert Einstein, born in Germany, is known for developing the theory of relativity.
[Extracted Triplets]:
Albert Einstein | country of birth | Germany;
Albert Einstein | developed | Theory of Relativity.
'''

# As a response generate only extracted triplets in the format, described above and do not include additional explanations of the obtained result.

EN_TRIPLETS_EXTRACTION_USER_PROMPT = \
    '''
[Text]:
{text}
'''

EN_TRIPLETS_ASSISTANT_PROMPT = \
    '''
[Extracted Triplets]:
'''

# == Prompts in Russian ==

RU_TRIPLETS_EXTRACTION_SYSTEM_PROMPT = \
    '''
Цель: Основная цель — тщательно собрать информацию из входных данных [Текст] и организовать эти данные в чёткий, структурированный граф знаний. Граф знаний состоит из набора триплетов. Каждый триплет содержит две сущности (субъект и объект) и одно отношение, связывающее их. Субъект — это сущность, которая совершает или подвергается действию, выраженному предикатом. Объект — это сущность, являющаяся фактическим объектом действия. Информацию, предоставляемую каждым предикатом, можно обобщить как триплет знаний вида «субъект | предикат | объект».

Требования к построению графа знаний:
1. Узлы должны отображать объекты или концепции, обычно одним или двумя словами. Субъекты и объекты могут быть именованными сущностями или концепциями, описывающими группу людей, событий или абстрактных объектов из графа знаний Викиданных.
2. Сложные объекты или концепции, такие как «Джон | должность | инженер в Google», должны быть разделены на простые, например, «Джон | должность | инженер» и «Джон | работа в | Google».
3. Длина триплета не должна превышать 7 слов.
4. Извлекайте только конкретные знания, любые предположения должны быть описаны как гипотезы. Например, из [Текст] «Джон набрал много очков и потенциально станет победителем» извлекайте «Джон | набрал много | очков», «Джон | может стать | победителем» и не извлекайте «Джон | станет | победителем».
3. Объект и субъект в триплете должны быть атомарными единицами, а связь может быть более сложной и длинной.
4. Не упускайте важную информацию. Если [Текст] — «книга повествует о рыцаре, которому нужно убить дракона», [Извлеченные триплеты] должны быть «книга | включает | рыцаря», «рыцарь | должен убить | дракона».
5. Можно извлечь несколько триплетов, содержащих информацию об одном и том же узле. Например: «кухня | содержит | яблоко», «кухня | содержит | стол», «яблоко | находится | на столе». Не упускайте такие связи.
6. Не используйте «none» в качестве объекта/субъекта в триплете.

[Извлеченные триплеты] следует возвращать в следующем формате:
subject_1 | relation_1 | object_1;
subject_2 | relation_2 | object_2;
...
subject_n | relation_n | object_n.

Примеры [Текста] и ожидаемых [Извлеченных триплетов] представлены в списке ниже:
#### Пример 1
[Текст]:
Альберт Эйнштейн, родившийся в Германии, известен разработкой теории относительности.
[Извлеченные триплеты]:
Альберт Эйнштейн | страна рождения | Германия;
Альберт Эйнштейн | разработал | Теорию относительности.
'''

RU_TRIPLETS_EXTRACTION_USER_PROMPT = \
    '''
[Текст]:
{text}
'''

RU_TRIPLETS_ASSISTANT_PROMPT = \
    '''
[Извлечённые триплеты]:
'''
