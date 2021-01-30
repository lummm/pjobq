FROM python:3.9.1-slim-buster AS base
ENV TINI_VERSION v0.19.0
WORKDIR /app
COPY ./requirements.txt ./requirements.txt
RUN apt update \
        && apt install --assume-yes \
        build-essential \
        libpq-dev \
        curl \
        && python -m pip install -r ./requirements.txt \
        && curl -L https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini -o /tini \
        && chmod +x /tini \
        && apt autoremove --assume-yes \
        build-essential \
        libpq-dev

COPY ./setup.py ./setup.py

        # first a test / mypy build
FROM base
ENV PGPASSWORD=test-pg-password
RUN python -m pip install mypy==0.800
COPY ./pjobq ./pjobq
RUN python -m mypy ./pjobq
RUN python -m pip install .
COPY ./test ./test
RUN python -m pip install ./test
RUN ./test/run.sh

        # lighter deploy build
FROM base
COPY ./pjobq ./pjobq
RUN python -m pip install .
COPY ./main.py ./main.py
ENTRYPOINT ["/tini", "/app/main.py"]
