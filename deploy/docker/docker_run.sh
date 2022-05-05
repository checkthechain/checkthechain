#!/bin/sh

: ${PYTHON_VERSION:='python3.10'}

docker run -it ctc/ctc-$PYTHON_VERSION

