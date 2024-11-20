apt-get update
apt-get upgrade

apt install python3.10-venv
apt install libicu-dev python3-icu pkg-config

python3.10 -m venv ../../.pai_venv
source ../../.pai_venv/bin/activate

pip install pysqlite3-binary chromadb aerospike kuzu pymongo neo4j
pip install dataclasses tqdm joblib
pip install pyicu pycld2 morfessor polyglot
pip install numpy pandas
pip install torch==2.4.1 transformers==4.40.0 sentence_transformers
pip install gigachat openai
