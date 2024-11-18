FROM m.menschikov/cuda:12.2.0-runtime-ubuntu22.04

LABEL maintainer="m.menschikov@skoltech.ru"

RUN apt-get update
RUN apt-get --assume-yes install pip
RUN apt-get --assume-yes install python3.10
RUN alias python=/usr/bin/python3.10

WORKDIR /home/workspace
ENV PYTHONPATH "${PYTHONPATH}:${APP_DIR}"

CMD ["sh", "-c", "sleep infinity"]
