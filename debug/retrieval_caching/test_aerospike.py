import sys
import aerospike

# TO CHANGE
BASEDIR = "/workspace"
# TO CHNAGE

sys.path.insert(0, BASEDIR)

from src.qa_pipeline.knowledge_retriever.cache import KeyValueStore

kv_store = KeyValueStore()

key = ('test', 'demo', 'foo')
out = kv_store.get_value_by_key(key)
kv_store.db_connector.close_connection()
print(out)
