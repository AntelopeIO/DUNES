#! /bin/bash

VARIANT=$1
if [[ ${VARIANT} == "deb" ]]; then
    if [ -z "$3" ]; then
        echo "Error, OS name and architecture missing for deb package type"
        exit 1
    else
        OS=$2
	ARCH=$3
    fi
fi

VERSION_NO_SUFFIX="1.0.0"
VERSION_SUFFIX=""
VERSION="$VERSION_NO_SUFFIX"-"$VERSION_SUFFIX"

# Using CMAKE_BINARY_DIR uses an absolute path and will break cross-vm building/download/make functionality
BUILD_DIR="../"

VENDOR="EOSNetworkFoundation"
PROJECT="DUNE"
DESC="Docker Utilities for Node Execution (DUNE) is a tool to abstract over Leap programs, CDT and other services/tools related to Antelope blockchains."
URL="https://github.com/AntelopeIO/DUNE"
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

if [[ ${VARIANT} == "brew" ]]; then
   . ./generate_bottle.sh
elif [[ ${VARIANT} == "deb" ]]; then
   . ./generate_deb.sh "${OS}" "${ARCH}"
else
   echo "Error, unknown package type. Use either ['brew', 'deb']."
   exit 2
fi

rm -r tmp || exit 1
