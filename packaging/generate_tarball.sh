#!/bin/bash

NAME=$1
DUNE_PREFIX="$PREFIX"/"$SUBPREFIX"
mkdir -p "$DUNE_PREFIX"/scripts
mkdir -p "$DUNE_PREFIX"/src
mkdir -p "$DUNE_PREFIX"/licenses

#echo ""$PREFIX" ** "$SUBPREFIX" ** "$DUNE_PREFIX""

# install
cp -R "$BUILD_DIR"/dune* "$DUNE_PREFIX" || exit 1
cp -R "$BUILD_DIR"/Dockerfile* "$DUNE_PREFIX" || exit 1
cp -R "$BUILD_DIR"/bootstrap* "$DUNE_PREFIX" || exit 1
cp -R "$BUILD_DIR"/src/* "$DUNE_PREFIX"/src || exit 1
cp -R "$BUILD_DIR"/scripts/* "$DUNE_PREFIX"/scripts || exit 1
cp -R "$BUILD_DIR"/LICENSE* "$DUNE_PREFIX"/licenses || exit 1

echo "Generating Tarball $NAME.tar.gz..."
tar -cvzf "$NAME".tar.gz ./"$PREFIX"/* || exit 1
rm -r "$PREFIX" || exit 1
