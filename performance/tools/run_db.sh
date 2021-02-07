#!/bin/bash

docker run -d --rm --net=host \
       --name performance-test-db \
       -e POSTGRES_PASSWORD=performance-testing \
       postgres:12.2
