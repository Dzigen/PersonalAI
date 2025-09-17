# == Prompts in English ==

EN_SWREMV_SYSTEM_PROMPT = '''
You are a linguist that process queries that will be sent to a search component. Sometimes, these queries on natural language contains redundant information or other noise, that makes it difficult to understand the main meaning/request/intention in the text. Your job is to reformulate given query with noise omition. As a result you must return modified query without noise.
Return only modified (from a unnecessary/noised information point of view) query; dont return enything else.
'''

EN_SWREMV_USER_PROMPT = '''
[Base query]
{query}
'''

EN_SWREMV_ASSISTANT_PROMPT = '''
[Denoised query]
'''

# == Prompts in Russian ==

RU_SWREMV_SYSTEM_PROMPT = '''
Вы — лингвист, который обрабатывает вопросы (queries) для их последующей отправки в поисковую QA-систему. Иногда эти вопросы на естественном языке содержат избыточную информацию или другой шум, который затрудняет понимание основного смысла/намерения в них. Ваша задача — переформулировать вопрос, исключив шум. В результате вы должны вернуть изменённый вопрос без шума.
Возвращайте только изменённый (с точки зрения ненужной/зашумлённой информации) вопрос; ничего больше не генерируйте.
'''

RU_SWREMV_USER_PROMPT = '''
[Исходный вопрос]
{query}
'''

RU_SWREMV_ASSISTANT_PROMPT = '''
[Модифицированный вопрос]
'''
