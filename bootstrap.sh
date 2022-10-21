#!/usr/bin/env bash

SDIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# for mac users
if [[ $(uname) == "Darwin" ]]; then
  GROUP_ID=200
fi

docker build --no-cache --build-arg USER_ID=0 --build-arg GROUP_ID=0 -f Dockerfile.unix -t dune $SDIR