FROM python:3.9.1-slim-buster

WORKDIR /app
# RUN apt update
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
RUN python -m pip install .

ENTRYPOINT ["python", "-m", "pjobq"]
