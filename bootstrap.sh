#!/usr/bin/env bash
set -o errexit -o pipefail -o noclobber -o nounset

getopt --test && echo "'getopt --test' failed in this environment." && exit 1

# Set SDIR to the path containing this script. Even if it's a symlink.
SDIR=$(dirname $(readlink -f "$0"))
cd "${SDIR}"

LONGOPTS=leap:,cdt:,release,push,help
OPTIONS=l:c:rph

PARSED=$(getopt --options=$OPTIONS --longoptions=$LONGOPTS --name "$0" -- "$@")

eval set -- "$PARSED"
LEAP_ARGUMENT=
CDT_ARGUMENT=
RELEASE_VERSION=
PUSH_VERSION=

usage="$(basename "$0") [-l|--leap=version] [-c|--cdt=version] [-r|--release]
where:
  -l, --leap=version
    sets the leap version
  -c, --cdt=version
    sets the CDT version
  -r, --release
    tag the image with the version reported by DUNES
  -p, --push
    with --release, push the release and latest images to ghcr.io"

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
            RELEASE_VERSION=$("${SDIR}"/dunes --version-short)
            echo "Release version: ${RELEASE_VERSION}"
            shift 1
            ;;
        -p|--push)
            PUSH_VERSION=$("${SDIR}"/dunes --version-short)
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

docker build --no-cache --build-arg USER_ID=0 --build-arg GROUP_ID="$GROUP_ID" $LEAP_ARGUMENT $CDT_ARGUMENT -f Dockerfile.unix -t dunes "$SDIR"

if [ -n "${RELEASE_VERSION}" ]; then
    docker tag dunes dunes:${RELEASE_VERSION}
    docker tag dunes ghcr.io/antelopeio/dunes:latest
    docker tag dunes ghcr.io/antelopeio/dunes:${RELEASE_VERSION}
    echo "Tagged image with latest and version '${RELEASE_VERSION}'."
    if [ -n "${PUSH_VERSION}" ]; then
        echo "Uploading to ghcr.io/antelopeio."
        docker push ghcr.io/antelopeio/dunes:latest
        docker push ghcr.io/antelopeio/dunes:${RELEASE_VERSION}
        echo "Uploaded latest and version '${RELEASE_VERSION}'."
    fi
fi

GIT_CMD='git rev-parse --short HEAD'
if ${GIT_CMD} > /dev/null 2> /dev/null; then
    COMMIT_HASH=$(${GIT_CMD})
    docker tag dunes dunes:${COMMIT_HASH}
    echo "Tagged image with commit hash '${COMMIT_HASH}'."
else
    echo "Could not determine git commit hash for this image. Not tagging."
fi
