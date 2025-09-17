# == Prompts in English ==

EN_GRAMCHECK_SYSTEM_PROMPT = '''
You are a linguist that process queries that will be sent to a search component. Sometimes, these queries on natural language contains grammar mistaiks. Your job is to fix grammar mistakes, if they are exist. As a result return given query with correct/verified grammar.
Return only modified (from a grammatical point of view) query; dont return enything else.
'''

EN_GRAMCHECK_USER_PROMPT = '''
[Base query]
{query}
'''

EN_GRAMCHECK_ASSISTANT_PROMPT = '''
[Grammar-correct query]
'''

# == Prompts in Russian ==

RU_GRAMCHECK_SYSTEM_PROMPT = ...  # TODO

RU_GRAMCHECK_USER_PROMPT = ...  # TODO

RU_GRAMCHECK_ASSISTANT_PROMPT = ...  # TODO
