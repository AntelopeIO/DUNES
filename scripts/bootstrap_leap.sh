#! /bin/sh -e
#
# install_leap.sh
#
# This script will install the leap .deb package with version as provided in $1.
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
    echo "arg 1, leap version, is empty."
    exit 1
fi
VERSION=$1
# Allow latest as an option in case insensitive fashion.
if [ "$(echo "${VERSION}" | tr "[:lower:]" "[:upper:])"" = "LATEST" ]; then
    VERSION=$(wget -q -O- https://api.github.com/repos/"$ORG"/leap/releases/latest | jq -r '.tag_name' | cut -c2-)
fi

# Currently, the dev and non-x86 binaries are experimental. This function will fetch them for us.
# No arguments, but VERSION and ORG must be set.
fetch_experimental_binaries () {

    # Sanity check ORG.
    if [ "$ORG" != "AntelopeIO" ]; then
        echo "Expected value of ORG is 'AntelopeIO', actual value is '${ORG}'. Exiting."
        exit 1
    fi

    # Name of the package we wish to get.
    CONTAINER_PACKAGE=AntelopeIO/experimental-binaries
    # An anonymous user token.
    GH_ANON_BEARER=$(curl -s "https://ghcr.io/token?service=registry.docker.io&scope=repository:${CONTAINER_PACKAGE}:pull" | jq -r .token)
    # The 'name' of the archive file we want to get.
    BLOB_NAME=$(curl -s -L -H "Authorization: Bearer ${GH_ANON_BEARER}" https://ghcr.io/v2/${CONTAINER_PACKAGE}/manifests/v"${VERSION}" | jq -r .layers[0].digest)
    # Get the file and extra its contents to the current directory.
    curl -s -L -H "Authorization: Bearer ${GH_ANON_BEARER}" https://ghcr.io/v2/${CONTAINER_PACKAGE}/blobs/"$BLOB_NAME" | tar -xz
}


# Remove any existing leap packages.
rm -f leap*ubuntu*.deb || true


# Package names are based on version and architecture.
# Additionally, some packages are ONLY part of the experimental binary. Download the files here.
case $VERSION in
    # Any versions of 3.1:
    "3.1"*)
        fetch_experimental_binaries
        if [ "$(uname -m)" = "x86_64" ]; then
            LEAP_PKG=leap-"${VERSION}"-ubuntu20.04-x86_64.deb
            LEAP_DEV_PKG=leap-dev-"${VERSION}"-ubuntu20.04-x86_64.deb
            wget https://github.com/"${ORG}"/leap/releases/download/v"${VERSION}"/"${LEAP_PKG}"
        else
            LEAP_PKG=leap-"${VERSION}"-ubuntu20.04-aarch64.deb
            LEAP_DEV_PKG=leap-dev-"${VERSION}"-ubuntu20.04-aarch64.deb
        fi;;

    # All others:
    *)
        fetch_experimental_binaries
        if [ "$(uname -m)" = "x86_64" ]; then
            LEAP_PKG=leap_"${VERSION}"-ubuntu20.04_amd64.deb
            LEAP_DEV_PKG=leap-dev_"${VERSION}"-ubuntu20.04_amd64.deb
            echo wget https://github.com/"${ORG}"/leap/releases/download/v"${VERSION}"/"${LEAP_PKG}"
            wget "https://github.com/${ORG}/leap/releases/download/v${VERSION}/${LEAP_PKG}"
        else
            LEAP_PKG=leap_"${VERSION}"-ubuntu20.04_arm64.deb
            LEAP_DEV_PKG=leap-dev_"${VERSION}"-ubuntu20.04_arm64.deb
        fi;;
esac


# Get the package and install it
apt --assume-yes --allow-downgrades install ./"${LEAP_PKG}" ./"${LEAP_DEV_PKG}"


# Remove any downloaded packages.
rm -f leap*ubuntu*.deb || true
