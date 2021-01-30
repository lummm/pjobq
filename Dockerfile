FROM python:3.9.1-slim-buster AS base
WORKDIR /app
COPY ./requirements.txt ./requirements.txt
RUN apt update \
        && apt install --assume-yes \
        build-essential \
        libpq-dev \
        && python -m pip install -r ./requirements.txt \
        && apt autoremove --assume-yes \
        build-essential \
        libpq-dev
COPY ./setup.py ./setup.py
COPY ./pjobq ./pjobq

        # first a test / mypy build
FROM base
ENV PGPASSWORD=test-pg-password
RUN python -m pip install mypy==0.800
RUN python -m mypy ./pjobq
RUN python -m pip install .
COPY ./test ./test
RUN find ./test -name '*.test.py' | xargs python

        # lighter deploy build
FROM base
RUN python -m pip install .
ENTRYPOINT ["python", "-m", "pjobq"]
