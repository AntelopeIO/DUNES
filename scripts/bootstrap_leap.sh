#! /bin/sh -e
. ./bootstrap_common.sh

LEAP_VERSION=$1

if [ -n "$LEAP_VERSION" ]; then
   FINAL_LEAP_VERSION="$LEAP_VERSION"
else
   FINAL_LEAP_VERSION=$(wget -q -O- https://api.github.com/repos/"$ORG"/leap/releases/latest | jq -r '.tag_name' | cut -c2-)
fi

CONTAINER_PACKAGE=AntelopeIO/experimental-binaries
GH_ANON_BEARER=$(curl -s "https://ghcr.io/token?service=registry.docker.io&scope=repository:${CONTAINER_PACKAGE}:pull" | jq -r .token)
curl -s -L -H "Authorization: Bearer ${GH_ANON_BEARER}" https://ghcr.io/v2/${CONTAINER_PACKAGE}/blobs/"$(curl -s -L -H "Authorization: Bearer ${GH_ANON_BEARER}" https://ghcr.io/v2/${CONTAINER_PACKAGE}/manifests/v"${FINAL_LEAP_VERSION}" | jq -r .layers[0].digest)" | tar -xz

case $FINAL_LEAP_VERSION in
   #up to 3.1
   "3.1"*) if [ "${ARCH}" = "x86_64" ]; then
      wget https://github.com/"${ORG}"/leap/releases/download/v"${FINAL_LEAP_VERSION}"/leap-"${FINAL_LEAP_VERSION}"-ubuntu20.04-x86_64.deb
      apt --assume-yes --allow-downgrades install ./leap-"${FINAL_LEAP_VERSION}"-ubuntu20.04-x86_64.deb
      apt --assume-yes --allow-downgrades install ./leap-dev-"${FINAL_LEAP_VERSION}"-ubuntu20.04-x86_64.deb
   else
      apt --assume-yes --allow-downgrades install ./leap-"${FINAL_LEAP_VERSION}"-ubuntu20.04-aarch64.deb
      apt --assume-yes --allow-downgrades install ./leap-dev-"${FINAL_LEAP_VERSION}"-ubuntu20.04-aarch64.deb
   fi;;

   #from 3.2
   *) if [ "${ARCH}" = "x86_64" ]; then
      wget https://github.com/"${ORG}"/leap/releases/download/v"${FINAL_LEAP_VERSION}"/leap_"${FINAL_LEAP_VERSION}"-ubuntu20.04_amd64.deb
      apt --assume-yes --allow-downgrades install ./leap_"${FINAL_LEAP_VERSION}"-ubuntu20.04_amd64.deb
      apt --assume-yes --allow-downgrades install ./leap-dev_"${FINAL_LEAP_VERSION}"-ubuntu20.04_amd64.deb
   else
      apt --assume-yes --allow-downgrades install ./leap_"${FINAL_LEAP_VERSION}"-ubuntu20.04_arm64.deb
      apt --assume-yes --allow-downgrades install ./leap-dev_"${FINAL_LEAP_VERSION}"-ubuntu20.04_arm64.deb
   fi;;
esac
