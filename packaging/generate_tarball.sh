#!/bin/bash -e

NAME=$1
DUNE_PREFIX="$PREFIX"/"$SUBPREFIX"
mkdir -p "$DUNE_PREFIX"/scripts
mkdir -p "$DUNE_PREFIX"/src
mkdir -p "$DUNE_PREFIX"/licenses

#echo ""$PREFIX" ** "$SUBPREFIX" ** "$DUNE_PREFIX""

# install
cp -R "$BUILD_DIR"/dune* "$DUNE_PREFIX"
cp -R "$BUILD_DIR"/Dockerfile* "$DUNE_PREFIX"
cp -R "$BUILD_DIR"/bootstrap* "$DUNE_PREFIX"
cp -R "$BUILD_DIR"/src/* "$DUNE_PREFIX"/src
cp -R "$BUILD_DIR"/scripts/* "$DUNE_PREFIX"/scripts
cp -R "$BUILD_DIR"/LICENSE* "$DUNE_PREFIX"/licenses

echo "Generating Tarball $NAME.tar.gz..."
tar -cvzf "$NAME".tar.gz ./"$PREFIX"/*
rm -r "$PREFIX"
