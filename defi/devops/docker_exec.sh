#!/bin/bash -xe

GIT_ROOT=$(git rev-parse --show-toplevel)
source $GIT_ROOT/docker_common/utils.sh

# Find the name of the container.
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)
DOCKER_NAME="$SCRIPT_DIR/docker_name.sh"
if [[ ! -e $SCRIPT_DIR ]]; then
    echo "Can't find $DOCKER_NAME"
    exit -1
fi;
source $DOCKER_NAME

# TODO(gp): Update to use exec_container
CONTAINER_ID=$(docker container ls | grep $IMAGE_NAME | awk '{print $1}')
OPTS="--user $(id -u):$(id -g)"
#OPTS=""
docker exec $OPTS -it $CONTAINER_ID bash
