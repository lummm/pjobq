#!/bin/bash

docker run -d --rm --net=host \
       -e POSTGRES_PASSWORD=performance-testing \
       postgres:12.2
