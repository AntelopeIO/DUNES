#! /bin/sh -e
. ./bootstrap_common.sh

rm -rf reference-contracts || true
git clone https://github.com/"${ORG}"/reference-contracts
cd reference-contracts
mkdir build
cd build
cmake ..
make -j4
