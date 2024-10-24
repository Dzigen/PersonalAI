import pytest

import sys
sys.path.insert(0, "../../")
from src.utils import NodeCreator, NodeType

@pytest.mark.parametrize("params, expected", [
    ({'name': 'abc', 'type': NodeType.object, 'add_stringified_node': True}, {'str_node': "abc"}),
    ({'name': 'abc', 'type': NodeType.object, 'add_stringified_node': True, 'prop': {
        'name': '1', 'type': '2', 'raw_time': '3', 'time': '123'}}, {'str_node': "123: abc"}),
    ({'name': 'abc', 'type': NodeType.object, 'add_stringified_node': False}, dict())
])
def test_craete_node(params, expected):
    node = NodeCreator.create(**params)

    # По-умолчанию ноде на назначается идентификатор
    if 'id' not in params:
        assert node.id is None
    else:
        assert node.id == params['id']

    # По запросу в ноду сохраняется её строковое представление.
    if params['add_stringified_node']:
        # При приведении ноды в строковое представление
        # в prop-поле не используются ключи с зарезервированными именами
        assert node.stringified == expected['str_node']
    else:
        assert node.stringified is None
