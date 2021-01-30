#!/bin/bash

set -e
for f in $(find ./test -name '*.test.py'); do
    python3.9 $f
done
