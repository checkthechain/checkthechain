#!/bin/sh

export DOCKER_BUILDKIT=1

DOCKER_BUILD_SCRIPT=$(realpath $0)
DOCKER_BUILD_DIR=$(realpath $(dirname DOCKER_BUILD_SCRIPT))
DOCKERFILE=$DOCKER_BUILD_DIR/Dockerfile
CTC_REPO=$(dirname $(dirname $DOCKER_BUILD_DIR))

echo "running build script:" $DOCKER_BUILD_SCRIPT
echo "using Dockerfile:" $DOCKERFILE
echo "using repository:" $CTC_REPO

docker build \
    -f $DOCKERFILE \
    -t ctc/ctc \
    $CTC_REPO
    #--no-cache \

