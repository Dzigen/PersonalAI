#!/bin/bash

echo "Creating volume dirs..."
cd volumes | mkdir chroma | mkdir kuzu | milvus | mkdir mongo | mkdir neo4j | mkdir neo4j | mkdir redis

echo "Creating containers for testing..."
docker-compose up -d neo4j
docker-compose up -d redis_cache
docker-compose up -d mongo_cache
docker-compose up -d milvus
echo "Waiting 15 sec for conteiners..."
sleep 15

mkdir tmp_coverage_log
mkdir tmp_coverage_log/integrational

echo "Running tests..."

pytest --cov=src --cov-report=html unit/
mv htmlcov/ tmp_coverage_log/unit

# memorize pipeline
pytest --cov=src.pipelines.memorize --cov-report=html integrational/memorize_pipeline/
mv htmlcov/ tmp_coverage_log/integrational/memorize_pipeline/

# db drivers
mkdir tmp_coverage_log/integrational/db_drivers
pytest --cov=src.db_drivers.graph_driver --cov-report=html integrational/db_drivers/graph_driver
mv htmlcov/ tmp_coverage_log/integrational/db_drivers/graph_driver
pytest --cov=src.db_drivers.vector_driver --cov-report=html integrational/db_drivers/vector_driver
mv htmlcov/ tmp_coverage_log/integrational/db_drivers/vector_driver
pytest --cov=src.db_drivers.kv_driver --cov-report=html integrational/db_drivers/kv_driver
mv htmlcov/ tmp_coverage_log/integrational/db_drivers/kv_driver
pytest --cov=src.db_drivers.kv_driver --cov-report=html integrational/db_drivers/tree_driver
mv htmlcov/ tmp_coverage_log/integrational/db_drivers/tree_driver

# kg model
pytest --cov=src.kg_model --cov-report=html integrational/kg_model/
mv htmlcov/ tmp_coverage_log/integrational/kg_model/

rm -rf log
rm .coverage

docker stop personalai_test_neo4j personalai_test_mongo personalai_test_redis
docker rm personalai_test_neo4j personalai_test_mongo personalai_test_redis
sudo rm -rf volumes/chroma volumes/kuzu volumes/milvus volumes/mongo volumes/neo4j volumes/redis

echo "Testing is completed!"
