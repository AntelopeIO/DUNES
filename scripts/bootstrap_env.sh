#! /bin/sh

ARCH=`uname -m`

ORG="eosnetworkfoundation"
NODE_VERSION="3.1.0-rc2"
CDT_VERSION="3.0.0-rc1"


CONTAINER_PACKAGE=eosnetworkfoundation/experimental-binaries
GH_ANON_BEARER=$(curl -s "https://ghcr.io/token?service=registry.docker.io&scope=repository:${CONTAINER_PACKAGE}:pull" | jq -r .token)
curl -s -L -H "Authorization: Bearer ${GH_ANON_BEARER}" https://ghcr.io/v2/${CONTAINER_PACKAGE}/blobs/$(curl -s -L -H "Authorization: Bearer ${GH_ANON_BEARER}" https://ghcr.io/v2/${CONTAINER_PACKAGE}/manifests/v3.1.0-rc2 | jq -r .layers[0].digest) | tar zx

if [ "${ARCH}" = "x86_64" ]; then
   wget https://github.com/${ORG}/mandel/releases/download/v${NODE_VERSION}/mandel-${NODE_VERSION}-ubuntu20.04-x86_64.deb
   apt install ./mandel-${NODE_VERSION}-ubuntu20.04-x86_64.deb
   #apt install ./mandel-dev-${NODE_VERSION}-ubuntu20.04-x86_64.deb
   wget https://github.com/${ORG}/mandel.cdt/releases/download/v${CDT_VERSION}/cdt_${CDT_VERSION}_amd64.deb
   apt install ./cdt_${CDT_VERSION}_amd64.deb
else
   apt install ./mandel-${NODE_VERSION}-ubuntu20.04-aarch64.deb
   apt install ./mandel-dev-${NODE_VERSION}-ubuntu20.04-aarch64.deb
   wget https://github.com/${ORG}/${CDT_REPO}/releases/download/v${CDT_VERSION}/cdt_${CDT_VERSION}_arm64.deb
   apt install ./cdt_${CDT_VERSION}_arm64.deb
fi

git clone https://github.com/eosnetworkfoundation/mandel-contracts 
cd mandel-contracts
git checkout main
mkdir build
cd build
cmake ..
make -j4