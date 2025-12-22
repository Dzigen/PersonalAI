from ..utils import GraphDBConnectionConfig
from ....utils.data_structs import NodeType, RelationType


DEFAULT_INMEMORYGRAPH_CONFIG = GraphDBConnectionConfig(
    params={
        'load_from_disk': False,
        'load_dump_name': None,
        'load_dump_dir': "./personalai_tmp/volumes/inmemory_graph",
        'save_on_disk': True, 'save_dump_dir': "./personalai_tmp/volumes/inmemory_graph",
        'rewrite': False
    }
)

DEFAULT_KUZU_CONFIG = GraphDBConnectionConfig(
    params={
        'path': "./personalai_tmp/volumes/kuzu_graph", 'buffer_pool_size': 1024**3,
        'table_type_map': {
            'relations': {'forward': {RelationType.simple.value: 'simple', RelationType.hyper.value: 'hyper_rel', RelationType.episodic.value: 'episodic_rel', RelationType.time.value: 'time_rel'}, },
            'nodes': {'forward': {NodeType.object.value: 'object', NodeType.hyper.value: 'hyper', NodeType.episodic.value: 'episodic', NodeType.time.value: 'time'}}
        }
    }
)

DEFAULT_NEO4J_CONFIG = GraphDBConnectionConfig(
    host='localhost', port=7687, params={'user': "neo4j", 'pwd': 'password'})


BG_NAMESPACE_CONFIG_TEMPLATE = '''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<!DOCTYPE properties SYSTEM "http://java.sun.com/dtd/properties.dtd">
<properties>
<entry key="com.bigdata.namespace.qqqqw.spo.com.bigdata.btree.BTree.branchingFactor">1024</entry>
<entry key="com.bigdata.rdf.store.AbstractTripleStore.textIndex">false</entry>
<entry key="com.bigdata.rdf.store.AbstractTripleStore.axiomsClass">com.bigdata.rdf.axioms.NoAxioms</entry>
<entry key="com.bigdata.rdf.sail.isolatableIndices">false</entry>
<entry key="com.bigdata.rdf.sail.truthMaintenance">false</entry>
<entry key="com.bigdata.rdf.store.AbstractTripleStore.justify">false</entry>
<entry key="com.bigdata.rdf.sail.namespace">{namespace_name}</entry>
<entry key="com.bigdata.rdf.store.AbstractTripleStore.quads">true</entry>
<entry key="com.bigdata.namespace.qqqqw.lex.com.bigdata.btree.BTree.branchingFactor">400</entry>
<entry key="com.bigdata.rdf.store.AbstractTripleStore.geoSpatial">false</entry>
<entry key="com.bigdata.rdf.store.AbstractTripleStore.statementIdentifiers">false</entry>
</properties>'''

DEFAULT_BLAZEGRAPH_CONFIG = GraphDBConnectionConfig(
    host='localhost', port=8889,
    db_info={'db': 'defaultpersonalaigraphdb', 'table': 'defaultpersonalaigraphtable'},
    params={'uri': 'http://personalai.org/', 'namespace_configuration': BG_NAMESPACE_CONFIG_TEMPLATE}
)
