import pytest
import sys
# TO CHANGE
PROJECT_BASE_DIR = '../'
TEST_VOLUME_DIR = './volumes'
sys.path.insert(0, PROJECT_BASE_DIR)

from src.kg_model.graph_model import GraphModel
from src.utils.data_structs import NodeType, RelationType
from src.db_drivers.graph_driver import GraphDriverConfig, GraphDBConnectionConfig
from src.kg_model import GraphModelConfig

@pytest.fixture(scope='package')
def graph_neo4j_config():
    config = GraphModelConfig(
        driver_config=GraphDriverConfig(
            db_vendor='neo4j',
            db_config=GraphDBConnectionConfig(
                host="localhost", port="7680", db_info={'db': 'testing', 'table': 'testing'},
                params={'user': "neo4j", 'pwd': 'password'}, need_to_clear=True)))
    return config


@pytest.fixture(scope='package')
def graph_inmemory_config():
    config = GraphModelConfig(
        driver_config=GraphDriverConfig(
            db_vendor='inmemory_graph',
            db_config=GraphDBConnectionConfig(
                db_info={'db': 'testing', 'table': 'testing'},
                params={
                    'load_from_disk': False,
                    'load_dump_name': None,
                    'load_dump_dir': f"{TEST_VOLUME_DIR}/inmemory_graph",
                    'save_on_disk': True, 'save_dump_dir': f"{TEST_VOLUME_DIR}/inmemory_graph",
                },
                need_to_clear=True)))
    return config


@pytest.fixture(scope='package')
def graph_kuzu_config():
    config = GraphModelConfig(
        driver_config=GraphDriverConfig(
            db_vendor='kuzu',
            db_config=GraphDBConnectionConfig(
                db_info={'db': 'testing', 'table': 'testing'},
                params={'path': f'{TEST_VOLUME_DIR}/kuzu', 'buffer_pool_size': 1024**3,
                        'table_type_map': {
                            'relations': {'forward': {RelationType.simple.value: 'simple', RelationType.hyper.value: 'hyper_rel', RelationType.episodic.value: 'episodic_rel'}, },
                            'nodes': {'forward': {NodeType.object.value: 'object', NodeType.hyper.value: 'hyper', NodeType.episodic.value: 'episodic'}}
                        }
                        },
                need_to_clear=True
            )
        )
    )
    return config


# ------------------------------#

@pytest.fixture(scope='package')
def available_graph_configs(
    graph_neo4j_config,
    graph_inmemory_config,
    graph_kuzu_config
):
    return {
        'neo4j': graph_neo4j_config,
        'inmemory_graph': graph_inmemory_config,
        'kuzu': graph_kuzu_config
    }

@pytest.fixture(scope='package')
def available_graph_models(available_graph_configs):
    return {graph_vendor: GraphModel(config) for graph_vendor, config in available_graph_configs.items()}


@pytest.fixture(scope='function')
def graph_model(available_graph_models, request):
    return available_graph_models[request.param]
