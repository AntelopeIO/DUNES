#! /bin/sh -e
. ./bootstrap_common.sh

rm -rf reference-contracts || true
git clone https://github.com/"${ORG}"/reference-contracts
cd reference-contracts
git checkout 074bc11394d13395e82015f6c41db32a67170d73
mkdir build
cd build
cmake ..
make -j4
