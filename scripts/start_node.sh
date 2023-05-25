#! /bin/bash

# 1 - data directory
# 2 - config.ini directory
# 3 - snapshot
# 4 - replay-blockchain option
# 5 - node name

nodeos --data-dir=$1 --config-dir=$2 $3 $4 >/app/$5.out 2>&1 &
