#! /bin/sh -e
#
# install_contracts.sh
#
# This script will install the reference-contracts with version as provided in $1.
# If $1 is 'latest', the latest release is used.
#

# Make sure we operate in the expected directory.
cd "$(dirname "$(readlink -f "$0")")"

# Sanity check
if [ -z "$ORG" ]; then
    ORG="AntelopeIO"
fi

# Sanity check version, set the variable.
if [ -z "$1" ]; then
    echo "arg 1, contract version, is empty."
    exit 1
fi
VERSION=$1
# Allow latest as an option in case insensitive fashion.
if [ "$(echo "${VERSION}" | tr "[:lower:]" "[:upper:]")" = "LATEST" ]; then
    VERSION=$(git ls-remote https://github.com/"${ORG}"/reference-contracts.git HEAD | cut -f 1)
fi


# Remove any existing contracsts.
rm -rf reference-contracts* || true


# Get the archive, extract the files, rename the directory, and remove the archive.
ARCHIVE_FILE="${VERSION}".tar.gz
wget https://github.com/"${ORG}"/reference-contracts/archive/"${ARCHIVE_FILE}"
tar xfz "${ARCHIVE_FILE}"
mv reference-contracts-"${VERSION}" reference-contracts
rm -f "${ARCHIVE_FILE}"

# Add version info into the directory:
echo "reference-contracts ${ORG} ${VERSION}" > reference-contracts/VERSION.DUNES.txt

# Make the build directory and switch to it
mkdir -p reference-contracts/build
cd reference-contracts/build

# cmake and build
cmake ..
make -j4
