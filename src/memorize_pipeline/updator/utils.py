from dataclasses import dataclass, field

from ...utils import Logger

REPLACE_THESIS_PROMPT = '''Тебе будет предоставлен список существующих тезисов и список новых тезисов. 
Тезисы обозначают факты о мире. Окружение меняется, поэтому некоторые тезисы из списка существующих тезисов можно заменить на один из новых тезисов. Например, игрок взял предмет из шкафчика, и существующий тезис «предмет находится в шкафчике» должен быть заменен новым тезисом «предмет находится в инвентаре».

Иногда тезисы, которые нужно заменить, отсутствуют:
Пример существующих тезисов: [«Золотой шкафчик открыт», «Комната K находится к западу от комната I», «Комната K имеет выход на восток»].
Пример новых тезисов: [«Комната T находится к северу от комната N», «Комната T имеет выход на юг»].
Пример замены: []. Здесь ничего заменять не нужно

Иногда несколько тезисов можно заменить одним:
Пример существующих тезисов: [«кухня имеет веник», «веник лежит на пол»].
Пример новых тезисов: [«веник находится в инвентарь»].
Пример замены: [«веник находится в инвентарь <- кухня содержит веник», «веник находится в инвентаре <- веник находится на полу»]. Потому что метла сменила местоположение с пола на кухне на инвентарь игрока.

Убедись, что тезисы заменяются только в том случае, если они содержат избыточную или противоречивую информацию об одном и том же аспекте сущности. Не следует заменять тезисы, если они предоставляют отличную или дополнительную информацию о сущности по сравнению с новыми тезисами. В частности, рассмотри отношения, свойства или контексты, описываемые каждым тезисом, и проверьте их соответствие перед заменой. Если есть неопределенность в том, следует ли заменить тезис, отдайте предпочтение сохранению существующего тезиса, а не его замене. При сравнении существующих и новых тезисов, если они относятся к разным аспектам или атрибутам сущностей, не заменяйте их. Замены должны происходить только в случае семантического дублирования между существующим и новым тезисами.
Пример существующих тезисов: [«яблоко нужно приготовить», «нож используется для нарезки», «яблоко было нарезано»].
Пример новых тезисов: [«яблоко лежит на столе», «кухня содержит нож», «яблоко было запечено»].
Пример замены: []. Заменять здесь нечего. Эти тезисы описывают разные свойства предметов, поэтому их не следует заменять. 

Еще один пример того, когда не следует заменять существующие тезисы:
Пример существующих тезисов: [«кисть используется для рисования»].
Пример новых тезисов: [«кисть находится в художественном классе»].
Пример замены: []. Заменять здесь нечего. Эти тезисы описывают разные свойства кисти, поэтому их не следует заменять. 

Повторяю, не заменяй тезисы, если они несут разную информацию о сущностях!!! Лучше оставить тезис, чем заменить тот, который несет важную информацию. Не утверждай, что тезис нужно заменить, если ты в этом не уверен!!!
Если ты обнаружил в существующих тезисах тезисы, которые семантически дублируют некоторые тезисы в новых тезисах, замени такие тезисы из существующих тезисов. Однако не заменяй тезисы, если они относятся к разным вещам. 
Для каждого тезиса, который вы хотите заменить, вы должны найти замену в новых тезисах. Если нет четкой замены, не заменяйте существующие тезисы.
Замены должны содержать информацию о тех же свойствах, что и заменяемые утверждения, но включать более свежую информацию.
Ты ДОЛЖЕН сохранить существующие тезисы, если они содержат уникальную или актуальную информацию о сущностях. 
Например, ты НЕ ДОЛЖЕН заменять тезис «бег осуществляется в кроссовках» на «кроссовки находятся в магазине».
####

Генерируй только список замен, описания не нужны.
Существующие тезисы: {ex_thesises}.
Новые тезисы: {new_thesises}.
####
Внимание! Замены должны формироваться строго в следующем формате: [«новый_тезис_1 <- устаревший_тезис_1»; «новый_тезис_2 <- устаревший_тезис_2»; ...], ты НЕ ДОЛЖЕН включать в ответ какие-либо описания.
Замена: '''

REPLACE_THESIS_PROMPT_ENG = '''You will be provided with list of existing thesises and list of new thesises. 
The thesises denote facts about the environment where the player moves. The player takes actions and the environment changes, so some thesises from the list of existing thesises can be replaced with one of the new thesises. For example, the player took the item from the locker and the existing thesis "item is in locker" should be replaced with the new thesis "item is in inventory".

Sometimes there are no thesises to replace:
Example of existing thesises: ["Golden locker is open", "Room K is west of Room I", "Room K has exit to east"]
Example of new thesises: ["Room T is north of Room N", "Room T has exit to south"]
Example of replacing: []. Nothisg to replace here

Sometimes several thesises can be replaced with one:
Example of existing thesises: ["kitchen contains broom", "broom is on floor"]
Example of new thesises: ["broom is in inventory"]
Example of replacing: ["broom is in inventory <- kitchen contains broom", "broom is in inventory <- broom is on floor"]. Because broom changed location from the floor in the kitchen to players inventory.

Ensure that thesises are only replaced if they contain redundant or conflicting information about the same aspect of an entity. Thesises should not be replaced if they provide distinct or complementary information about entities compared to the new thesises. Specifically, consider the relationships, properties, or contexts described by each thesis and verify that they align before replacement. If there is uncertainty about whether a thesis should be replaced, prioritize retaining the existing thesis over replacing it. When comparing existing and new thesises, if they refer to different aspects or attributes of entities, do not replace them. Replacements should only occur when there is semantic duplication between an existing thesis and a new thesis.
Example of existing thesises: ["apple need to be cooked", 'knife used for cutting', 'apple has been sliced']
Example of new thesises: ["apple is on table", 'kitchen contains knife', 'apple has beed grilled']
Example of replacing: []. Nothing to replace here. These thesises describe different properties of items, so they should not be replaced. 

Another example of when not to replase existung thesises:
Example of existing thesises: ["brush is used for painting"]
Example of new thesises: ["brush is in art class"]
Example of replacing: []. Nothing to replace here. These thesises describe different properties of brush, so they should not be replaced. 

I repeat, do not replace thesises if they carry differend type of information about entities!!! It is better to leave a thesis, than to replace the one that has important information. Do not state that thesis needs to be replaced if you are not sure!!!
If you find thesis in Existing thesises which semantically duplicate some thesis in New thesises, replace such thesis from Existing thesises. However do not replace thesis if they refer to different things. 
For every thesis you want to replace you must find replacement from new thesises. If there is no clear replacement, you must not replace existing thesis.
The replacements should contain information about the same properties as the statements being replaced, but must include more recent information.
You MUST save existing thesis if it contains unique or actual information about entities. 
For example, you MUST NOT replace thesis "running is done with sneakers" with "sneakers located at store".
####

Generate only list of replacing, no descriptions are needed.
Existing thesises: {ex_thesises}.
New thesises: {new_thesises}.
####
Warning! Replacing must be generated strictly in following format: ["new_thesis_1 <- outdated_thesis_1"; "new_thesis_2 <- outdated_thesis_2"; ...], you MUST NOT include any descriptions in answer.
Replacing: '''

REPLACE_SIMPLE_PROMPT = """Тебе будет предоставлен список существующих и список новых триплетов. Тройки имеют следующий формат: «субъект, отношение, объект».
Триплеты обозначают факты о мире. Окружение меняется, поэтому некоторые триплеты из списка существующих триплетов могут быть заменены одним из новых триплетов. Например, игрок взял предмет из шкафчика, и существующая тройка «предмет, находится в, шкафчик» должна быть заменена на новую тройку «предмет, находится в, инвентарь».

Иногда триплеты для замены отсутствуют:
Пример существующих триплетов: «Золотой шкафчик, состояние, открытый»; „Комната K, находится к западу от, комната I“; „Комната K, имеет выход, восточный“.
Пример новых триплетов: «Комната T, находится к северу от, комната N»; „Комната T, имеет выход на, юг“.
Пример замены: []. Заменять здесь нечего

Иногда несколько триплетов можно заменить одним:
Пример существующих троек: "кухня, содержит, веник"; "веник, находится на, пол".
Пример новых троек: "метла, находится в, инвентарь".
Пример замены: [[«кухня, содержит, веник» -> «веник, находится в, инвентарь»], [«веник, находится на, пол» -> «веник, находится в, инвентарь»]]. Потому что веник сменил местоположение с пола на кухне на инвентарь игрока.

Убедитесь, что триплеты заменяются только в том случае, если они содержат избыточную или противоречивую информацию об одном и том же аспекте сущности. Триплеты не должны заменяться, если они предоставляют отличную или дополнительную информацию о сущностях по сравнению с новыми триплетами. В частности, рассмотрите отношения, свойства или контексты, описываемые каждой тройкой, и убедитесь, что они совпадают перед заменой. Если существует неопределенность в отношении того, следует ли заменять триплет, отдайте предпочтение сохранению существующего триплета, а не его замене. При сравнении существующих и новых триплетов, если они относятся к разным аспектам или атрибутам сущностей, не заменяйте их. Замены должны происходить только в случае семантического дублирования между существующим и новым триплетом.
Пример существующих триплетов: 'яблоко, будет, приготовлено', 'нож, используется для, нарезка', 'яблоко, было, нарезано'.
Пример новых триплетов: "яблоко, лежит на, столе", "кухня, содержит, нож", "яблоко, было, запечено".
Пример замены: []. Заменять здесь нечего. Эти триплеты описывают разные свойства предметов, поэтому их не следует заменять. 

Еще один пример того, когда не следует заменять существующие тройки:
Пример существующих триплетов: "кисть, используется для, рисования".
Пример новых триплетов: "кисть, находится в, художественный класс".
Пример замены: []. Заменять здесь нечего. Эти триплеты описывают разные свойства кисти, поэтому их не следует заменять. 

Повторяю, не заменяйте триплеты, если они несут разную информацию о сущностях!!! Лучше оставить триплет, чем заменить тот, который несет важную информацию. Не утверждайте, что триплет нужно заменить, если вы в этом не уверены!!!
Если вы нашли триплет в существующих триплетах, который семантически дублирует некоторый триплет в новых триплетах, замените такой триплет из существующих триплетов. Однако не заменяйте триплеты, если они относятся к разным вещам. 
####

Генерировать только замены, описания не нужны.
Существующие триплеты: {ex_triplets}.
Новые триплеты: {new_triplets}.
####
Внимание! Замены должны формироваться строго в следующем формате: [[устаревший_триплет_1 -> актуальный_триплет_1], [устаревший_триплет_2 -> актуальный_триплет_2], ...], вы НЕ ДОЛЖНЫ включать в ответ никаких описаний.
Замена: """

REPLACE_SIMPLE_PROMPT_ENG = """You will be provided with list of existing triplets and list of new triplets. Triplets are in the following format: "subject, relation, object".
The triplets denote facts about the environment where the player moves. The player takes actions and the environment changes, so some triplets from the list of existing triplets can be replaced with one of the new triplets. For example, the player took the item from the locker and the existing triplet "item, is in, locker" should be replaced with the new triplet "item, is in, inventory".

Sometimes there are no triplets to replace:
Example of existing triplets: "Golden locker, state, open"; "Room K, is west of, Room I"; "Room K, has exit, east".
Example of new triplets: "Room T, is north of, Room N"; "Room T, has exit, south".
Example of replacing: []. Nothisg to replace here

Sometimes several triplets can be replaced with one:
Example of existing triplets: "kitchen, contains, broom"; "broom, is on, floor".
Example of new triplets: "broom, is in, inventory".
Example of replacing: [["kitchen, contains, broom" -> "broom, is in, inventory"], ["broom, is on, floor" -> "broom, is in, inventory"]]. Because broom changed location from the floor in the kitchen to players inventory.

Ensure that triplets are only replaced if they contain redundant or conflicting information about the same aspect of an entity. Triplets should not be replaced if they provide distinct or complementary information about entities compared to the new triplets. Specifically, consider the relationships, properties, or contexts described by each triplet and verify that they align before replacement. If there is uncertainty about whether a triplet should be replaced, prioritize retaining the existing triplet over replacing it. When comparing existing and new triplets, if they refer to different aspects or attributes of entities, do not replace them. Replacements should only occur when there is semantic duplication between an existing triplet and a new triplet.
Example of existing triplets: "apple, to be, cooked", 'knife, used for, cutting', 'apple, has been, sliced'
Example of new triplets: "apple, is on, table", 'kitchen, contsins, knife', 'apple, has beed, grilled'.
Example of replacing: []. Nothing to replace here. These triplets describe different properties of items, so they should not be replaced. 

Another example of when not to replase existung triplets:
Example of existing triplets: "brush, used for, painting".
Example of new triplets: "brush, is in, art class".
Example of replacing: []. Nothing to replace here. These triplets describe different properties of brush, so they should not be replaced. 

I repeat, do not replace triplets, if they carry differend type of information about entities!!! It is better to leave a tripplet, than to replace the one that has important information. Do not state that triplet needs to be replaced if you are not sure!!!
If you find triplet in Existing triplets which semantically duplicate some triplet in New triplets, replace such triplet from Existing triplets. However do not replace triplets if they refer to different things. 
####

Generate only replacing, no descriptions are needed.
Existing triplets: {ex_triplets}.
New triplets: {new_triplets}.
####
Warning! Replacing must be generated strictly in following format: [[outdated_triplet_1 -> actual_triplet_1], [outdated_triplet_2 -> actual_triplet_2], ...], you MUST NOT include any descriptions in answer.
Replacing: """

log_path = "debug"