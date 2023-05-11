#!/bin/bash -e

NAME=$1
DUNE_PREFIX="$PREFIX"/"$SUBPREFIX"
mkdir -p "$DUNE_PREFIX"/scripts
mkdir -p "$DUNE_PREFIX"/src
mkdir -p "$DUNE_PREFIX"/licenses
mkdir -p "$DUNE_PREFIX"/tests
mkdir -p "$DUNE_PREFIX"/plugin_example
mkdir -p "$DUNE_PREFIX"/docs

#echo ""$PREFIX" ** "$SUBPREFIX" ** "$DUNE_PREFIX""

# install
cp -R "$BUILD_DIR"/dune* "$DUNE_PREFIX"
cp -R "$BUILD_DIR"/Dockerfile* "$DUNE_PREFIX"
cp -R "$BUILD_DIR"/bootstrap* "$DUNE_PREFIX"
cp -R "$BUILD_DIR"/src/* "$DUNE_PREFIX"/src
cp -R "$BUILD_DIR"/scripts/* "$DUNE_PREFIX"/scripts
cp -R "$BUILD_DIR"/LICENSE* "$DUNE_PREFIX"/licenses
cp -R "$BUILD_DIR"/tests/* "$DUNE_PREFIX"/tests
cp -R "$BUILD_DIR"/plugin_example/* "$DUNE_PREFIX"/plugin_example
cp -R "$BUILD_DIR"/docs/* "$DUNE_PREFIX"/docs
cp -R "$BUILD_DIR"/README* "$DUNE_PREFIX"
# Add symbolic link
mkdir ./usr/bin
ln -s /"$DUNE_PREFIX/dune" ./usr/bin/antelopeio-dune

echo "Generating Tarball $NAME.tar.gz..."
tar -cvzf "$NAME".tar.gz ./"$PREFIX"/*
rm -r "$PREFIX"
