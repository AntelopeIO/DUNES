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

SCRIPT=$(readlink -f "$0")
DIR=$(dirname "$SCRIPT")
cd $DIR
export DIR

DUNES_EXE=$(dirname ${DIR})/dune

VERSION_NO_SUFFIX=$(${DUNES_EXE} --version-short)
VERSION_SUFFIX="dev"
VERSION="$VERSION_NO_SUFFIX"-"$VERSION_SUFFIX"


# Using CMAKE_BINARY_DIR uses an absolute path and will break cross-vm building/download/make functionality
BUILD_DIR="$DIR/../"

VENDOR="EOSNetworkFoundation"
PROJECT="dunes"
DESC="Docker Utilities for Node Execution and Subsystems (DUNES) is a tool to abstract over Leap programs, CDT and other services/tools related to Antelope blockchains."
URL="https://github.com/AntelopeIO/DUNES"
EMAIL="support@eosnetwork.com"

export BUILD_DIR
export VERSION_NO_SUFFIX
export VERSION_SUFFIX
export VERSION
export VENDOR
export PROJECT
export DESC
export URL
export EMAIL

mkdir -p tmp

if [[ ${VARIANT} == "deb" ]]; then
   . "$DIR"/generate_deb.sh "${OS}"
elif [[ ${VARIANT} == "rpm" ]]; then
   . "$DIR"/generate_rpm.sh
else
   echo "Error, unknown package type. Use either ['brew', 'deb', 'rpm']."
   exit 2
fi

rm -r tmp
