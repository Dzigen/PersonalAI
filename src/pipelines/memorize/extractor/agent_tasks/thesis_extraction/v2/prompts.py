# == Prompts in English ==

EN_THESISES_EXTRACTION_SYSTEM_PROMPT = \
    '''
Objective: The main goal is to meticulously gather information from input [Text] and organize this data into a clear, structured knowledge graph.

Requirements for building a knowledge graph:
1. Entities must depict concepts, similar to Wikipedia nodes. Entities must not include verbs and any other words which described motion, properties and etc. All the entities must be the real world objects or abstract concept. Use a structured thesises format to capture data. For example, from [Text] "Albert Einstein, born in Germany, is known for developing the theory of relativity" [Extracted thesises] should be "Albert Einstein was born in Germany | ['Albert Einstein', 'Germany', 'birth']", "Albert Einstein developed Theory of Relativity | ['Albert Einstein', 'developing', 'Theory of Relativity'].".
2. Thesises MUST BE comprehension and consistent, so you can make them in form of sentense. You better make a much longer thesis than split it into two which inconsistent separately. For example, you better extract thesis "North exit from kitchen is blocked by door" than "kitchen has door" and "north exit is blocked by door" because without context of kitchen "north exit is blocked by door" can be related to every room at home.
3. You should extract only concrete knowledges, any assumptions must be described as hypothesis. For example, from [Text] "John have scored many points and potentially will be winner" [Extracted thesises] should be "John scored many points | ['John', 'scoring', 'point']", "John could be winner | ['John', 'winner']." and you should not extract "John will be winner | ['John', 'winner'].".
4. Remember that nodes must be an atomary units while thesis can be more complex and long.
5. Do not miss important information. If [Text] is "book involves story about knight, who needs to kill a dragon", thesises should be "book involves knight", "knight needs to kill dragon".
6. Several thesises can be extracted, that contain information about the same node. For example "kitchen contains apple", "kitchen contains table", "apple is on table". Do not miss this type of connections.
7. Do not use "none" as one of the entities.

[Extracted thesises] should be returned in the following format:
thesis_1 | [list of entites for thesis_1];
thesis_2 | [list of entites for thesis_2];
...
thesis_n | [list of entites for thesis_n].
'''

# As a response generate only extracted thesises in the format, described above and do not include additional explanations of the obtained result.

EN_THESISES_EXTRACTION_USER_PROMPT = \
    '''
[Text]:
{text}
'''

EN_THESISES_EXTRACTION_ASSISTANT_PROMPT = \
    '''
[Extracted thesises]:
'''

# == Prompts in Russian ==

RU_THESISES_EXTRACTION_SYSTEM_PROMPT = \
    '''
Цель: Основная цель — тщательно собрать информацию из входных данных [Текст] и организовать эти данные в чёткую, структурированную графу знаний.

Требования к построению графа знаний:
1. Сущности должны отображать концепции, аналогичные узлам Википедии. Сущности не должны содержать глаголов и любых других слов, описывающих движение, свойства и т. д. Все сущности должны быть объектами реального мира или абстрактными концепциями. Используйте структурированный формат тезисов для сбора данных. Например, из [Текст] «Альберт Эйнштейн, родившийся в Германии, известен разработкой теории относительности». [Извлечённые тезисы] должны выглядеть так: «Альберт Эйнштейн родился в Германии | ['Альберт Эйнштейн', 'Германия', 'рождение']», «Альберт Эйнштейн разработал теорию относительности | ['Альберт Эйнштейн', 'разработка', 'Теория относительности']». 2. Тезисы ДОЛЖНЫ БЫТЬ понятными и последовательными, чтобы их можно было сформулировать в виде предложений. Лучше сделать более длинный тезис, чем разбивать его на два, которые по отдельности несовместимы. Например, лучше выделить тезис «Северный выход из кухни заблокирован дверью», чем «В кухне есть дверь» и «Северный выход заблокирован дверью», поскольку без контекста кухни тезис «Северный выход заблокирован дверью» можно связать с любой комнатой в доме.
3. Следует извлекать только конкретные знания, любые предположения должны быть описаны как гипотезы. Например, из [Текст] «Джон набрал много очков и потенциально станет победителем» [Извлеченные тезисы] следует сделать «Джон набрал много очков | ['Джон', 'набранное', 'очко']», «Джон может стать победителем | ['Джон', 'победитель']». Не следует извлекать «Джон станет победителем | ['Джон', 'победитель']». 4. Помните, что узлы должны быть атомарными единицами, в то время как тезисы могут быть более сложными и длинными.
5. Не упускайте важную информацию. Если [Текст] — «книга содержит историю о рыцаре, которому нужно убить дракона», тезисы должны быть «книга содержит историю о рыцаре», «рыцарю нужно убить дракона».
6. Можно извлечь несколько тезисов, содержащих информацию об одном и том же узле. Например, «кухня содержит яблоко», «кухня содержит стол», «яблоко на столе». Не упускайте такие связи.
7. Не используйте «none» в качестве одной из сущностей.

[Извлеченные тезисы] должны быть возвращены в следующем формате:
тезис_1 | [список сущностей для тезиса_1];
тезис_2 | [список сущностей для тезиса_2];
...
тезис_n | [список сущностей для тезиса_n].
'''

RU_THESISES_EXTRACTION_USER_PROMPT = \
    '''
[Текст]:
{text}
'''

RU_THESISES_EXTRACTION_ASSISTANT_PROMPT = \
    '''
[Извлечённые тезисы]:
'''
