from ..conftest import *


@pytest.fixture(scope='function')
def personalai_inst(available_personaai_instances, request):
    return available_personaai_instances[request.param]