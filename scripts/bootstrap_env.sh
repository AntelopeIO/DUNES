#! /bin/sh

ARCH=`uname -m`

# TODO change to eosnetworkfoundation after releases are made
ORG="larryk85"

# TODO change to 3.1.0
NODE_VERSION="v1.0"
NODE_PKG_NAME="mandel_3.0.5"

# TODO change to 3.0.0
CDT_VERSION="v1.0"
CDT_PKG_NAME="cdt_1.8.1"

# TODO change to mandel
NODE_REPO="ENF-Binaries"
# TODO change to mandel.cdt
CDT_REPO="ENF-Binaries"
CONTRACTS_REPO="mandel-contracts"

if [ "${ARCH}" = "x86_64" ]; then
   wget https://github.com/${ORG}/${NODE_REPO}/releases/download/${NODE_VERSION}/${NODE_PKG_NAME}_amd64.deb
   apt install ./${NODE_PKG_NAME}_amd64.deb

   wget https://github.com/${ORG}/${CDT_REPO}/releases/download/${CDT_VERSION}/${CDT_PKG_NAME}_amd64.deb
   apt install ./${CDT_PKG_NAME}_amd64.deb
else
   wget https://github.com/${ORG}/${NODE_REPO}/releases/download/${NODE_VERSION}/${NODE_PKG_NAME}_arm64.deb
   apt install ./${NODE_PKG_NAME}_arm64.deb

   wget https://github.com/${ORG}/${CDT_REPO}/releases/download/${CDT_VERSION}/${CDT_PKG_NAME}_arm64.deb
   apt install ./${CDT_PKG_NAME}_arm64.deb
fi


git clone https://github.com/eosnetworkfoundation/mandel-contracts 
cd mandel-contracts
git pull
git checkout larryk85/mandel-update
mkdir build
cd build
cmake ..
make -j4