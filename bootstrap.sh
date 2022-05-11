#! /usr/bin/bash

SDIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
docker build --no-cache -t dune $SDIR