#! /bin/sh

ARCH=`uname -m`

ORG="AntelopeIO"
NODE_VERSION="3.1.0-rc4"
CDT_VERSION="3.0.0-rc2"


CONTAINER_PACKAGE=AntelopeIO/experimental-binaries
GH_ANON_BEARER=$(curl -s "https://ghcr.io/token?service=registry.docker.io&scope=repository:${CONTAINER_PACKAGE}:pull" | jq -r .token)
curl -s -L -H "Authorization: Bearer ${GH_ANON_BEARER}" https://ghcr.io/v2/${CONTAINER_PACKAGE}/blobs/$(curl -s -L -H "Authorization: Bearer ${GH_ANON_BEARER}" https://ghcr.io/v2/${CONTAINER_PACKAGE}/manifests/v3.1.0-rc2 | jq -r .layers[0].digest) | tar zx

if [ "${ARCH}" = "x86_64" ]; then
   wget https://github.com/${ORG}/leap/releases/download/v${NODE_VERSION}/leap-${NODE_VERSION}-ubuntu20.04-x86_64.deb
   apt install ./leap-${NODE_VERSION}-ubuntu20.04-x86_64.deb
   apt install ./leap-dev-${NODE_VERSION}-ubuntu20.04-x86_64.deb
   wget https://github.com/${ORG}/cdt/releases/download/v${CDT_VERSION}/cdt_${CDT_VERSION}_amd64.deb
   apt install ./cdt_${CDT_VERSION}_amd64.deb
else
   apt install ./leap-${NODE_VERSION}-ubuntu20.04-aarch64.deb
   apt install ./leap-dev-${NODE_VERSION}-ubuntu20.04-aarch64.deb
   wget https://github.com/${ORG}/cdt/releases/download/v${CDT_VERSION}/cdt_${CDT_VERSION}_arm64.deb
   apt install ./cdt_${CDT_VERSION}_arm64.deb
fi

git clone https://github.com/eosnetworkfoundation/eos-system-contracts 
cd eos-system-contracts
git checkout main
mkdir build
cd build
cmake ..
make -j4
