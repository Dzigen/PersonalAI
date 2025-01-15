mkdir tmp_coverage_log
mkdir tmp_coverage_log/integrational

pytest --cov=src --cov-report=html unit/
mv htmlcov/ tmp_coverage_log/unit

pytest --cov=src.pipelines.memorize --cov-report=html integrational/memorize_pipeline/
mv htmlcov/ tmp_coverage_log/integrational/memorize_pipeline/

mkdir tmp_coverage_log/integrational/db_drivers

pytest --cov=src.db_drivers.graph_driver --cov-report=html integrational/db_drivers/graph_driver
mv htmlcov/ tmp_coverage_log/integrational/db_drivers/graph_driver

pytest --cov=src.db_drivers.vector_driver --cov-report=html integrational/db_drivers/vector_driver
mv htmlcov/ tmp_coverage_log/integrational/db_drivers/vector_driver

pytest --cov=src.db_drivers.kv_driver --cov-report=html integrational/db_drivers/kv_driver
mv htmlcov/ tmp_coverage_log/integrational/db_drivers/kv_driver

pytest --cov=src.kg_model --cov-report=html integrational/kg_model/
mv htmlcov/ tmp_coverage_log/integrational/kg_model/

rm -rf log
rm .coverage
