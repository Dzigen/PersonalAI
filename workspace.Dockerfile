FROM m.menschikov/cuda:12.2.0-runtime-ubuntu22.04

LABEL maintainer="m.menschikov@skoltech.ru"

RUN apt-get update
RUN apt-get --assume-yes install pip
RUN apt-get --assume-yes install python3
RUN apt-get --assume-yes install libicu-dev python3-icu
RUN alias python=/usr/bin/python3

RUN pip install dataclasses tqdm joblib
RUN pip install numpy pandas
RUN pip install torch==2.4.1 transformers==4.40.0 sentence_transformers
RUN pip install pysqlite3-binary chromadb==0.5.3 aerospike==15.1.0 kuzu pymongo neo4j redis
RUN pip install gigachat==0.1.17 openai
RUN pip install pytest
RUN pip install pyicu pycld2 morfessor polyglot

RUN useradd -rm -d /home/m.menschikov -s /bin/bash -g root -G sudo -u 4200235 m.menschikov

WORKDIR /home/m.menschikov/workspace

ARG APP_DIR=/home/m.menschikov/workspace
ENV PYTHONPATH "${PYTHONPATH}:${APP_DIR}"

USER m.menschikov
#USER root

CMD ["sh", "-c", "sleep infinity"]
#CMD ["sh", "-c", "ls -la /workspace && cd '/workspace/experiments/qa_astar_pipeline (new_graph) (exp #2.1)/' && python3 answer_generation.py"]
