FROM robd003/python3.10:latest

LABEL maintainer="m.menschikov@skoltech.ru"

# RUN apt-get clean
# RUN rm -rf /var/lib/apt/lists/*
# RUN apt-get clean
# RUN apt-get --assume-yes update
# RUN apt-get --assume-yes upgrade

RUN python3.10 -m pip install --upgrade pip
RUN python3.10 -m pip install PyYAML

CMD ["sh", "-c", "sleep infinity"]
