#! /bin/sh -e
. ./bootstrap_common.sh

CDT_VERSION=$1

if [ -n "$CDT_VERSION" ]; then
   FINAL_CDT_VERSION="$CDT_VERSION"
else
   FINAL_CDT_VERSION=$(wget -q -O- https://api.github.com/repos/"$ORG"/cdt/releases/latest | jq -r '.tag_name' | cut -c2-)
fi


if [ "${ARCH}" = "x86_64" ]; then
   wget https://github.com/"${ORG}"/cdt/releases/download/v"${FINAL_CDT_VERSION}"/cdt_"${FINAL_CDT_VERSION}"_amd64.deb
   apt --assume-yes --allow-downgrades install ./cdt_"${FINAL_CDT_VERSION}"_amd64.deb
else
   wget https://github.com/"${ORG}"/cdt/releases/download/v"${FINAL_CDT_VERSION}"/cdt_"${FINAL_CDT_VERSION}"_arm64.deb
   apt --assume-yes --allow-downgrades install ./cdt_"${FINAL_CDT_VERSION}"_arm64.deb
fi
