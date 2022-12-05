#! /bin/sh -e

./bootstrap_leap.sh "$LEAP_VERSION"
./bootstrap_cdt.sh "$CDT_VERSION"
./bootstrap_contracts.sh
