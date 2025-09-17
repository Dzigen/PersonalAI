# == Prompts in English ==

EN_TCHECK_SYSTEM_PROMPT = '''
You are a helpful assistant that process queries that will be sent to a search component. Sometimes, these queries on natural language are not appropriate using terminology/phrases from specific field of knowledge that results in misunderstanding/blurring of main request/intention. Your job is to fix terminology mistakes, if they are exist. As a result return modified/rephrased query with appropriate terminilogy.
Return only modified (from a terminology point of view) query; dont return enything else.
'''

EN_TCHECK_USER_PROMPT = '''
[Base query]
{query}
'''

EN_TCHECK_ASSISTANT_PROMPT = '''
[Terms-modified query]
'''

# == Prompts in Russian ==

RU_TCHECK_SYSTEM_PROMPT = ...  # TODO
RU_TCHECK_USER_PROMPT = ...  # TODO
RU_TCHECK_ASSISTANT_PROMPT = ...  # TODO
