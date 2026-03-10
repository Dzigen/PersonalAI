KGENV_FILE_PATH= ... # .env TO CHANGE

docker compose --env-file=$KGENV_FILE_PATH up -d workspace

OR

docker compose --env-file=$KGENV_FILE_PATH up -d neo4j qdrant opensearch mongo redis