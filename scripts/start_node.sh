#! /bin/sh

# 1 - data directory
# 2 - config.ini directory
# 3 - snapshot
# 4 - node name

nodeos --data-dir=$1 --config-dir=$2 $3 &> /home/www-data/$4.out
