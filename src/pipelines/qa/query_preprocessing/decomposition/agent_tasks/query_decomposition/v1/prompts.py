# == Prompts in English ==

EN_QD_SYSTEM_PROMPT = \
    '''
You are a helpful assistant that prepares queries that will be sent to a search component. Sometimes, these queries are complex: contains multiple independent intents/requests. Your job is to simplify complex queries into multiple queries that can be answered in isolation to eachother.

Generate simple sub-questions in the following format:
- <sub-query1>
- <sub-query2>
- <sub-query...>
- <sub-queryN>

Example:
[Base question]
Did Microsoft or Google make more money last year?
[Decomposed Questions]
- How much profit did Microsoft make last year?
- How much profit did Google make last year?'''

EN_QD_USER_PROMPT = \
    '''
[Base question]
{query}
'''
EN_QD_ASSISTANT_PROMPT = \
    '''
[Decomposed questions]
'''

# == Prompts in Russian ==

RU_QD_SYSTEM_PROMPT = \
    '''
Вы — полезный помощник, который обрабатывает вопросы (queries) для их последующей отправки в поисковую QA-систему. Иногда эти вопросы сложные: содержат несколько независимых намерений/запросов. Ваша задача — упростить сложный вопрос до нескольких под-вопросов, на которые можно ответить независимо друг от друга.

Сгенерируй набор простых под-вопросов в ​​следующем формате:
- <под-вопрос1>
- <под-вопрос2>
- <под-вопрос...>
- <под-вопросN>

Пример:
[Исходный вопрос]
Кто заработал больше: Microsoft или Google — в прошлом году?

[[Под-вопросы, в результате декомпозии исходного вопроса]
- Какую прибыль Microsoft получила в прошлом году?
- Какую прибыль Google получила в прошлом году?
'''

RU_QD_USER_PROMPT = \
    '''
[Исходный вопрос]
{query}
'''

RU_QD_ASSISTANT_PROMPT = \
    '''
[Под-вопросы, в результате декомпозии исходного вопроса]
'''
