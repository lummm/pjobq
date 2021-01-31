#!/bin/bash
# THIS SHOULD BE RUN FROM THE `integration` directory

docker build -t pjobq-it-test .
docker-compose down
docker-compose run pjobq-it-test
if [[ "$?" != "0" ]]; then
    docker-compose logs
fi
