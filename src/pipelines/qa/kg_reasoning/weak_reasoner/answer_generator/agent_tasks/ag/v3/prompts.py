### PROMPT IN ENGLISH ###

EN_SIMPLEAG_SYSTEM_PROMPT = \
    """
You are a system that is trying to generate an [Answer] for a given [Question], based on provided [Contexts] in a list format. If there is no relevant information in a given [Contexts] for generating the suitable answer or the [Contexts] is "<|Empty|>", then you should generate the following: "<|NotEnoughtInfo|>". Before generating the final answer you should present your [Chain of thoughts] that lead to the [Answer].

The format you must match for generating response is presented below:
[Chain of thoughts]: <chain-of-thoughts>
[Answer]: <final-answer>
,where <chain-of-thoughts> is your reasoning path based on given [Question] and [Contexts] that concludes to the [Answer] and <final-answer> is your final [Answer] to the [Question].

Examples of [Questions], [Contexts] and expected [Answers] are presented in a list below:
#### Example 1
[Example Question]: Whose opinions from Anthony and Grace about devices are most similar to Faith's?
[Example Contexts]:
- Xiaomi (kind: device) opinion (person: Anthony; opinion: hard) maintenance point (kind: feature)
- mate30pro (kind: device) opinion (person: Anthony; opinion: not as good as) signal (kind: feature)
- iPhone (kind: device) opinion (person: Anthony; opinion: not as good as) signal (kind: feature)
- Xiaomi 12 (kind: device) opinion (person: Grace; opinion: beat) charging speed (kind: feature)
- Xiaomi (kind: device) opinion (person: Faith; opinion: problem) product control (kind: feature)
- k30s (kind: device) opinion (person: Faith; opinion: not as good) film effect (kind: feature)
- red rice (kind: device) opinion (person: Faith; opinion: not as good) film effect (kind: feature)
[Example Chain of thoughts]: The task is to compare Anthony's and Grace's opinions to Faith's opinions about devices. Faith has two types of opinions: "problem" with the Xiaomi device and "not as good" with both k30s and red rice devices. We will look for similar expressions of dissatisfaction from Anthony and Grace. Grace's opinion about Xiaomi 12 is "beat", which is not similar to any of Faith's negative opinions. Anthony's opinions include "hard" for Xiaomi and "not as good as" for mate30pro and iPhone with respect to the signal feature. "Not as good as" matches Faith's "not as good".
[Example Answer]: Anthony
#### Example 2
[Example Question]: Whose opinions from Amanda and Arianna about manufacturers are most similar to Joshua's?
[Example Contexts]:
- Xiaomi 12 (kind: device) opinion (person: Grace; opinion: beat) charging speed (kind: feature)
- Xiaomi (kind: device) opinion (person: Faith; opinion: problem) product control (kind: feature)
- k30s (kind: device) opinion (person: Faith; opinion: not as good) film effect (kind: feature)
[Example Chain of thoughts]: The task is to compare Amanda's and Arianna's opinions to Joshua's opinions about manufacturers. The provided contexts does not allow to determine which opinions from Amanda and Arianna about manufacturers are most similar to Joshua's.
[Example Answer]: <|NotEnoughtInfo|>
#### Example 3
[Example Question]: The majority of speakers have positive, neutral or negative sentiment about signal of Apple?
[Example Contexts]:
<|Empty|>
[Example Chain of thoughts]: The information for a give question is not provided.
[Example Answer]: <|NotEnoughtInfo|>
#### Example 4
[Example Question]: The majority of speakers have positive, neutral or negative sentiment about signal of Apple?
[Example Context]:
- 15.11.2020: Apple (kind: device) opinion (person: Alejandro; opinion: beats) battery life (kind: feature)
- 30.12.2020: Apple (kind: device) opinion (person: Jacqueline; opinion: Nice pictures taken) taking pictures (kind: feature)
- 30.12.2020: Apple (kind: device) opinion (person: Diego; opinion: Doesnt overheat) heat radiation (kind: feature)
- 30.12.2020: Apple (kind: device) opinion (person: Lily; opinion: Not bad) configuration of other processors (kind: feature)
- 25.11.2020: Apple (kind: device) opinion (person: Margaret; opinion: Pictures turn blurry) taking pictures (kind: feature)
- 25.11.2020: Apple (kind: device) opinion (person: Amber; opinion: Really unhelpful) sales (kind: feature)
- 25.11.2020: Apple (kind: device) opinion (person: Jessica; opinion: Always been strong) signal (kind: feature)
- 25.11.2020: Apple (kind: device) opinion (person: Bernard; opinion: No lag) play games (kind: feature)
[Example Chain of thoughts]: To determine the sentiment about the signal of Apple, we need to find the opinions specifically related to the "signal" feature of Apple. From the provided info, only Jessica's opinion mentions the signal: "Always been strong". This is a positive sentiment. Since there's only one opinion regarding the signal, the majority sentiment is positive.
[Example Answer]: Positive

--------------------------------------------------------------------------------------------------------------------------------

"""

EN_SIMPLEAG_USER_PROMPT = \
    """
Generate [Answer] for the [Question] based on provided [Contexts].

[Question]: {q}
[Contexts]:
{c}"""

EN_SIMPLEAG_ASSISTANT_PROMPT = \
    """
[Chain of thoughts]: """

### PROMPT IN RUSSIAN ###

RU_SIMPLEAG_SYSTEM_PROMPT = \
    """
Вы — система, которая пытается сгенерировать [Ответ] на заданный [Вопрос] на основе предоставленных [Контекстов] в формате списка. Если в заданном [Контексте] нет релевантной информации для генерации подходящего ответа или [Контекст] имеет значение "<|Empty|>", вам следует сгенерировать следующее: "<|NotEnoughtInfo|>". Перед генерацией окончательного ответа необходимо представить [Цепочку мыслей], ведущую к [Ответу].

Формат, которому необходимо следовать для генерации ответа, представлен ниже:
[Цепочка мыслей]: <цепочка мыслей>
[Ответ]: <окончательный ответ>
, где <цепочка мыслей> — это ваш путь рассуждений, основанный на заданном [Вопросе] и [Контекстах], который приводит к [Ответу], а <окончательный ответ> — ваш окончательный [Ответ] на [Вопрос].

Примеры [Вопросов], [Контекстов] и ожидаемых [Ответов] представлены в списке ниже:
#### Пример 1
[Пример вопроса]: Чьи мнения Энтони и Грейс об устройствах наиболее схожи с мнением Фейт?
[Примеры контекстов]:
- Xiaomi (kind: устройство) мнение (person: Энтони; opinion: сложно) точка обслуживания (kind: feature)
- mate30pro (kind: устройство) мнение (person: Энтони; opinion: не так хорошо, как) сигнал (kind: feature)
- iPhone (kind: устройство) мнение (person: Энтони; opinion: не так хорошо, как) сигнал (kind: feature)
- Xiaomi 12 (kind: устройство) мнение (person: Грейс; opinion: бит) скорость зарядки (kind: feature)
- Xiaomi (kind: устройство) мнение (person: Вера; opinion: проблема) управление продуктом (kind: feature)
- k30s (kind: устройство) мнение (person: Вера; opinion: не так хорошо) эффект пленки (kind: feature)
- красный рис (kind: устройство) мнение (person: Вера; opinion: не так хорошо) эффект пленки (kind: feature)
[Пример цепочки мыслей]: Задача — сравнить Энтони и Мнение Грейс о мнении Фейт об устройствах. У Фейт есть два типа мнений: «проблема» с устройством Xiaomi и «не очень хорошо» как с K30s, так и с Red Rice. Мы будем искать похожие выражения недовольства у Энтони и Грейс. Мнение Грейс о Xiaomi 12 — «плохо», что не похоже ни на одно из негативных мнений Фейт. Мнения Энтони включают «плохо» для Xiaomi и «не так хорошо, как» для Mate 30 Pro и iPhone в отношении сигнала. «Не так хорошо, как» совпадает с «не так хорошо» у Фейт.
[Пример ответа]: Энтони
#### Пример 2
[Пример вопроса]: Чьи мнения Аманды и Арианны о производителях наиболее схожи с мнением Джошуа?
[Примеры контекстов]:
- Xiaomi 12 (kind: устройство) мнение (person: Грейс; opinion: бит) скорость зарядки (kind: feature)
- Xiaomi (kind: устройство) мнение (person: Вера; opinion: проблема) управление продуктом (kind: feature)
- K30s (kind: устройство) мнение (person: Вера; opinion: не так хорош) эффект от плёнки (kind: feature)
[Пример цепочки мыслей]: Задача — сравнить мнения Аманды и Арианны с мнениями Джошуа о производителях. Предоставленные контексты не позволяют определить, какие мнения Аманды и Арианны о производителях наиболее близки мнению Джошуа.
[Пример ответа]: <|NotEnoughtInfo|>
#### Пример 3
[Пример вопроса]: Большинство опрошенных положительно, нейтрально или отрицательно относятся к сигналу Apple?
[Примеры контекстов]:
<|Пусто|>
[Пример цепочки мыслей]: Информация для данного вопроса не предоставлена.
[Пример ответа]: <|NotEnoughtInfo|>
#### Пример 4
[Пример вопроса]: Большинство опрошенных положительно, нейтрально или отрицательно относятся к сигналу Apple?
[Пример контекста]:
- 15.11.2020: Apple (kind: устройство) мнение (person: Алехандро; opinion: beats) время работы батареи (kind: feature)
- 30.12.2020: Apple (kind: устройство) мнение (person: Жаклин; opinion: Хорошие снимки) Фотографирование (kind: feature)
- 30.12.2020: Apple (kind: устройство) мнение (person: Диего; opinion: Не перегревается) Тепловое излучение (kind: feature)
- 30.12.2020: Apple (kind: устройство) мнение (person: Лили; opinion: Неплохо) Конфигурация других процессоров (kind: feature)
- 25.11.2020: Apple (kind: устройство) мнение (person: Маргарет; opinion: Снимки получаются размытыми) Фотографирование (kind: feature)
- 25.11.2020: Apple (kind: устройство) мнение (person: Эмбер; opinion: Действительно бесполезно) продажи (kind: feature)
- 25.11.2020: Apple (kind: устройство) мнение (person: Джессика; opinion: Всегда был сильным) сигнал (kind: feature)
- 25.11.2020: Apple (kind: устройство) мнение (person: Бернард; opinion: Без задержек) играть в игры (kind: feature)
[Пример цепочки мыслей]: Чтобы определить отношение к сигналу Apple, нам нужно найти мнения, непосредственно связанные с функцией Apple «сигнал». Из предоставленной информации только мнение Джессики упоминает сигнал: «Всегда был сильным». Это положительное отношение. Поскольку существует только одно мнение о сигнале, большинство настроений положительно.
[Пример ответа]: Положительное

--------------------------------------------------------------------------------------------------------------------------------

"""

RU_SIMPLEAG_USER_PROMPT = \
    """Сгенерируй [Ответ] на [Вопрос], опираясь на приведенную информацию в [Контексте].
[Вопрос]: {q}
[Контекст]:
{c}"""

RU_SIMPLEAG_ASSISTANT_PROMPT = \
    """
[Цепочка рассуждений]: """
