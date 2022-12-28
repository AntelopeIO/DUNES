#! /bin/bash -e

VARIANT=$1
if [[ ${VARIANT} == "deb" ]]; then
    if [ -z "$2" ]; then
        echo "Error, OS name missing for deb package type"
        exit 1
    else
        OS=$2
    fi
fi

VERSION_NO_SUFFIX="1.0.0"
VERSION_SUFFIX="dev"
VERSION="$VERSION_NO_SUFFIX"-"$VERSION_SUFFIX"

SCRIPT=$(readlink -f "$0")
DIR=$(dirname "$SCRIPT")
export DIR

ORIGINAL_DIR=`pwd`
cd $DIR

# Using CMAKE_BINARY_DIR uses an absolute path and will break cross-vm building/download/make functionality
BUILD_DIR="$DIR/../"

VENDOR="EOSNetworkFoundation"
PROJECT_PREFIX="ANTELOPEIO"
PROJECT="DUNE"
DESC="Docker Utilities for Node Execution (DUNE) is a tool to abstract over Leap programs, CDT and other services/tools related to Antelope blockchains."
URL="https://github.com/AntelopeIO/DUNE"
EMAIL="support@eosnetwork.com"

export BUILD_DIR
export VERSION_NO_SUFFIX
export VERSION_SUFFIX
export VERSION
export VENDOR
export PROJECT_PREFIX
export PROJECT
export DESC
export URL
export EMAIL

mkdir -p tmp

if [[ ${VARIANT} == "deb" ]]; then
   . "$DIR"/generate_deb.sh "${OS}"
else
   echo "Error, unknown package type. Use either ['brew', 'deb']."
   exit 2
fi

rm -r tmp
