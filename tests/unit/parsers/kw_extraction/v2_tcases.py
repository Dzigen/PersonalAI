KWE_PARSE_V2_TEST_CASES = [
    # пустая строк
    ('', [], False),
    # одна сущность
    ('asd', ['asd'], False),
    # несколько сущностей
    ('asd | qwe | zxc', ['asd', 'qwe', 'zxc'], False)
]
