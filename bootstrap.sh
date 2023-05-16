#!/usr/bin/env bash
set -o errexit -o pipefail -o noclobber -o nounset

set -v

getopt --test && echo "'getopt --test' failed in this environment." && exit 1

# Set SDIR to the path containing this script. Even if it's a symlink.
SDIR=$(dirname $(readlink -f "$0"))


LONGOPTS=leap:,cdt:,release,help
OPTIONS=l:c:rh

PARSED=$(getopt --options=$OPTIONS --longoptions=$LONGOPTS --name "$0" -- "$@")

eval set -- "$PARSED"
LEAP_ARGUMENT=
CDT_ARGUMENT=
RELEASE_VERSION=

usage="$(basename "$0") [-l|--leap=version] [-c|--cdt=version] [-r|--release]
where:
  -l, --leap=version
    sets the leap version
  -c, --cdt=version
    sets the CDT version
  -r, --release
    tag the image with the version reported by DUNES"

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
        -r|--release)
            RELEASE_VERSION=$(${SDIR}/dune --version-short)
            echo "Release version: ${RELEASE_VERSION}"
            shift 1
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


GROUP_ID=0
# for mac users
if [[ $(uname) == "Darwin" ]]; then
  GROUP_ID=200
fi

docker build --no-cache --build-arg USER_ID=0 --build-arg GROUP_ID="$GROUP_ID" $LEAP_ARGUMENT $CDT_ARGUMENT -f Dockerfile.unix -t dune "$SDIR"

if [ -n "${RELEASE_VERSION}" ]; then
    docker tag dune dune:${RELEASE_VERSION}
    docker tag dune ghcr.io/antelopeio/dune:latest
    docker tag dune ghcr.io/antelopeio/dune:${RELEASE_VERSION}
    echo "Tagged image with latest and version '${RELEASE_VERSION}'."
fi

GIT_CMD="git -C ${SDIR} rev-parse --short HEAD"
if ${GIT_CMD} > /dev/null 2> /dev/null; then
    COMMIT_HASH=$(${GIT_CMD})
    docker tag dune dune:${COMMIT_HASH}
    echo "Tagged image with commit hash '${COMMIT_HASH}'."
else
    echo "Could not determine git commit hash for this image. Not tagging."
fi
