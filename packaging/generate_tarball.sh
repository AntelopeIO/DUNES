#!/bin/bash -e

NAME=$1
DUNES_PREFIX="$PREFIX"/"$SUBPREFIX"
mkdir -p "$DUNES_PREFIX"/scripts
mkdir -p "$DUNES_PREFIX"/src
mkdir -p "$DUNES_PREFIX"/licenses
mkdir -p "$DUNES_PREFIX"/tests
mkdir -p "$DUNES_PREFIX"/plugin_example
mkdir -p "$DUNES_PREFIX"/docs

#echo ""$PREFIX" ** "$SUBPREFIX" ** "$DUNES_PREFIX""

# install
cp -R "$BUILD_DIR"/dunes* "$DUNES_PREFIX"
cp -R "$BUILD_DIR"/Dockerfile* "$DUNES_PREFIX"
cp -R "$BUILD_DIR"/bootstrap* "$DUNES_PREFIX"
cp -R "$BUILD_DIR"/src/* "$DUNES_PREFIX"/src
cp -R "$BUILD_DIR"/scripts/* "$DUNES_PREFIX"/scripts
cp -R "$BUILD_DIR"/LICENSE* "$DUNES_PREFIX"/licenses
cp -R "$BUILD_DIR"/tests/* "$DUNES_PREFIX"/tests
cp -R "$BUILD_DIR"/plugin_example/* "$DUNES_PREFIX"/plugin_example
cp -R "$BUILD_DIR"/docs/* "$DUNES_PREFIX"/docs
cp -R "$BUILD_DIR"/README* "$DUNES_PREFIX"
# Add symbolic link
mkdir ./usr/bin
ln -s /"$DUNES_PREFIX/dunes" ./usr/bin/dunes

echo "Generating Tarball $NAME.tar.gz..."
tar -cvzf "$NAME".tar.gz ./"$PREFIX"/*
rm -r "$PREFIX"
