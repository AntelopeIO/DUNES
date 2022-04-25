#! /usr/bin/bash

# 1 - data directory
# 2 - config.ini directory
# 3 - enable stale production
# 4 - producer
# 5 - node name

nodeos --data-dir=$1 --config-dir=$2 $3 --producer-name=$4 &> /app/nodes/$5.out
