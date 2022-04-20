#!/bin/sh

cd ../src/ctc

mypy \
    --disallow-untyped-defs \
    --no-implicit-optional \
    --strict-equality \
    ./

# not used because mypy has produces false positives:
# --warn-redundant-casts \
# --warn-unused-ignores \
