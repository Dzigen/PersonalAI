FROM m.menschikov/cuda:12.2.0-runtime-ubuntu22.04

LABEL maintainer="m.menschikov@skoltech.ru"

RUN apt-get update
RUN apt-get --assume-yes install pip
RUN apt-get --assume-yes install python3.10
RUN alias python=/usr/bin/python3.10

USER m.menschikov
WORKDIR /home/m.menschikov/workspace

ARG APP_DIR=/home/m.menschikov/workspace
ENV PYTHONPATH "${PYTHONPATH}:${APP_DIR}"

CMD ["sh", "-c", "sleep infinity"]
