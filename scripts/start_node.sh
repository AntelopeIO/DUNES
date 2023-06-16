#! /bin/bash

# 1 - data directory
# 2 - config.ini directory
# 3 - snapshot
# 4 - node name
# 5 - replay-blockchain option

nodeos --data-dir=$1 --config-dir=$2 $3 $5 >/app/$4.out 2>&1 &
