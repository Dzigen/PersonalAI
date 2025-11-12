import pytest
import sys
# TO CHANGE
PROJECT_BASE_DIR = '../'
sys.path.insert(0, PROJECT_BASE_DIR)


from src.kg_model import KnowledgeGraphModel
from src.pipelines.qa import QAPipelineConfig, QAPipeline
from .cases import POPULATED_QAPIPELINE_TEST_CASES

@pytest.mark.parametrize("qa_config, query, kg_model", POPULATED_QAPIPELINE_TEST_CASES, indirect=['kg_model'])
def test_qapipeline(qa_config: QAPipelineConfig, query: str, kg_model: KnowledgeGraphModel):
    qa_pipeline = QAPipeline(kg_model, qa_config, kg_model.cache_config)

    _, info = qa_pipeline.answer(query)
    assert info.status.value == 0
