#!/usr/bin/env bash

SDIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

GROUP_ID=$(id -g ${USER})
# for mac users
if [[ $(uname) == "Darwin" ]]; then
  GROUP_ID=200
fi
docker build --no-cache --build-arg USER_ID=$(id -u ${USER}) --build-arg GROUP_ID=${GROUP_ID} -f Dockerfile.unix -t dune $SDIR
