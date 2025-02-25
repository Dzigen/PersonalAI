GOOD_RESPONSE1 = 'a, b, c; d, e, f.'
GOOD_RESPONSE2 = 'a, b, c.'
BAD_RESPONSE1 = 'a, b, c; d e f.'
BAD_RESPONSE2 = 'a, b, c, d, e, f.'

ETRIPLETS_PARSE_V1_TEST_CASES = [
    # пустая строка
    ("",None, True),
    # валидный формат (один триплет)
    (GOOD_RESPONSE2, [('a','b','c')], False),
    # валидный формат (несколько триплетов)
    (GOOD_RESPONSE1, [('a','b','c'), ('d','e','f')], False),
    # невалидный формат (;)
    (BAD_RESPONSE1, None, True),
    # невалидный формат (,)
    (BAD_RESPONSE2, None, True)
]
