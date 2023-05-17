#!/usr/bin/env bash
set -o errexit -o pipefail -o noclobber -o nounset

getopt --test && echo "'getopt --test' failed in this environment." && exit 1

LONGOPTS=leap:,cdt:,help
OPTIONS=l:c:h

PARSED=$(getopt --options=$OPTIONS --longoptions=$LONGOPTS --name "$0" -- "$@")

eval set -- "$PARSED"
LEAP_ARGUMENT=
CDT_ARGUMENT=

usage="$(basename "$0") [-l|--leap=version] [-c|--cdt=version]
where:
  -l, --leap=version
    sets the leap version
  -c, --cdt=version
    sets the CDT version"

while true; do
    case "$1" in
        -l|--leap) # Specifies leap version, i.e. --leap=3.1.0
            LEAP_ARGUMENT="--build-arg LEAP_VERSION=$2"
            shift 2
            ;;
        -c|--cdt) # Specifies cdt version, i.e. --cdt=3.0.0
            CDT_ARGUMENT="--build-arg CDT_VERSION=$2"
            shift 2
            ;;
        --)
            shift
            break
            ;;
        -h | --help) # Display help.
            echo -e "$usage"
            exit 0
            ;;
    esac
done

SDIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

GROUP_ID=0
# for mac users
if [[ $(uname) == "Darwin" ]]; then
  GROUP_ID=200
fi

docker build --no-cache --build-arg USER_ID=0 --build-arg GROUP_ID="$GROUP_ID" $LEAP_ARGUMENT $CDT_ARGUMENT -f Dockerfile.unix -t dunes "$SDIR"
