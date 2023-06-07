#! /bin/sh -e
#
# install_cdt.sh
#
# This script will install the CDT .deb package with version as provided in $1.
# If $1 is 'latest', the latest release is used.
#

# Make sure we operate in the expected directory.
cd $(dirname $(readlink -f "$0"))

# Sanity check
if [ -z "$ORG" ]; then
    ORG="AntelopeIO"
fi

# Sanity check version, set the variable.
if [ -z "$1" ]; then
    echo "arg 1, cdt version, is empty."
    exit 1
fi
VERSION=$1
# Allow latest as an option in case insensitive fashion.
if [ "$(echo ${VERSION} | tr [:lower:] [:upper:])" = "LATEST" ]; then
    VERSION=$(wget -q -O- https://api.github.com/repos/"$ORG"/cdt/releases/latest | jq -r '.tag_name' | cut -c2-)
fi

# Determine architecture and set package arch
PARCH="amd64"
if [ "$(uname -m)" != "x86_64" ]; then
    PARCH="arm64"
fi


# Remove any existing cdt packages.
rm -f cdt_*.deb || true


# get the package and install it.
CDT_PKG=cdt_"${VERSION}"_"${PARCH}".deb
wget https://github.com/"${ORG}"/cdt/releases/download/v"${VERSION}"/"${CDT_PKG}"
apt --assume-yes --allow-downgrades install ./"${CDT_PKG}"

# remove any downloaded files
rm -f ./"${CDT_PKG}" || true
