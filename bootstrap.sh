#!/usr/bin/env bash
set -o errexit -o pipefail -o noclobber -o nounset

getopt --test && echo "'getopt --test' failed in this environment." && exit 1

# Set SDIR to the path containing this script. Even if it's a symlink.
SDIR=$(dirname "$(readlink -f "$0")")
cd "${SDIR}"

# Forward definitions
LEAP_ARGUMENT=
CDT_ARGUMENT=
RELEASE_VERSION=
PUSH_VERSION=
TAG_OVERRIDE=



# Command line decoding begins.

LONGOPTS=leap:,cdt:,release,push,tag:,help
OPTIONS=l:c:rph

PARSED=$(getopt --options=$OPTIONS --longoptions=$LONGOPTS --name "$0" -- "$@")

eval set -- "$PARSED"

usage="$(basename "$0") [-l|--leap=version] [-c|--cdt=version] [-r|--release [-p|--push]] [--tag]
where:
  -l, --leap=version
    sets the leap version
  -c, --cdt=version
    sets the CDT version
  -r, --release
    tag the image with the version reported by DUNES
  -p, --push
    with --release, push the release and latest images to ghcr.io
  --tag=tag
    ONLY tag the image with the user provided tag"


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
        --tag)
            TAG_OVERRIDE="dunes:$2"
            echo "Overriding default tagging with $TAG_OVERRIDE"
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
# Command line decoding completed.



# Set group ID. Note the difference for mac users.
GROUP_ID=0
if [[ $(uname) == "Darwin" ]]; then
    # Set group ID to 200 for mac
    GROUP_ID=200
fi


# Function to call docker build
# $1 : tag to apply to the build
docker_build() {

    if [ -z "$1" ]; then
        echo "docker_build requires an argument"
        exit 1
    fi

    # Note: LEAP_ARGUMENT and CDT_ARGUMENT are either empty or they include '--build-arg'
    docker build --no-cache --build-arg USER_ID=0 --build-arg GROUP_ID="$GROUP_ID" $LEAP_ARGUMENT $CDT_ARGUMENT -f Dockerfile.unix -t "$1" "$SDIR"
}


# Test for tag override. Note that an override will exit without tagging latest, version, or short hash.
if [ -n "${TAG_OVERRIDE}" ]; then
    # Currently, tag override conflicts with release.
    if [ -n "${RELEASE_VERSION}" ]; then
        echo "--tag conflicts with --release, exiting"
        exit 1
    fi
    # Call the build with the override tag.
    docker_build "${TAG_OVERRIDE}"
    # Tag override exits before normal build process.
    exit 0
fi


# Call the build with our default tag.
docker_build dunes

# Test for release command.
if [ -n "${RELEASE_VERSION}" ]; then
    # Make the additional release tags.
    docker tag dunes dunes:"${RELEASE_VERSION}"
    docker tag dunes ghcr.io/antelopeio/dunes:latest
    docker tag dunes ghcr.io/antelopeio/dunes:"${RELEASE_VERSION}"
    echo "Tagged image with latest and version '${RELEASE_VERSION}'."
    # Test for push command.
    if [ -n "${PUSH_VERSION}" ]; then
        # Push the images.
        echo "Uploading to ghcr.io/antelopeio."
        docker push ghcr.io/antelopeio/dunes:latest
        docker push ghcr.io/antelopeio/dunes:"${RELEASE_VERSION}"
        echo "Uploaded latest and version '${RELEASE_VERSION}'."
    fi
fi

# Test to see if this is git repository.
GIT_CMD='git rev-parse --short HEAD'
if ${GIT_CMD} > /dev/null 2> /dev/null; then
    # Tag the image with the short commit hash.
    COMMIT_HASH=$(${GIT_CMD})
    docker tag dunes dunes:"${COMMIT_HASH}"
    echo "Tagged image with commit hash '${COMMIT_HASH}'."
else
    # Inform the user we did not tag with a commit hash.
    echo "Could not determine git commit hash for this image. Not tagging."
fi
