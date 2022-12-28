#!/bin/bash -e

OS=$1

PREFIX="usr"
SPREFIX="$PREFIX"
SUBPREFIX="opt/$PROJECT/$VERSION"
SSUBPREFIX="opt\/$PROJECT\/$VERSION"
RELEASE="$VERSION_SUFFIX"

# default release to "1" if there is no suffix
if [[ -z $RELEASE ]]; then
  RELEASE="1"
fi

PACKAGE_NAME=$(echo "$PROJECT_PREFIX-$PROJECT" | tr '[:upper:]' '[:lower:]')
NAME="${PACKAGE_NAME}_${VERSION_NO_SUFFIX}-${RELEASE}_all"

mkdir -p "$PROJECT"/DEBIAN
echo "Package: $PACKAGE_NAME
Version: $VERSION_NO_SUFFIX-$RELEASE
Depends: python3, docker | docker-ce-cli, curl, wget
Section: devel
Priority: optional
Architecture: all
Homepage: $URL
Maintainer: $EMAIL
Description: $DESC" &> "$PROJECT"/DEBIAN/control
cat "$PROJECT"/DEBIAN/control

export PREFIX
export SUBPREFIX
export SPREFIX
export SSUBPREFIX

. "$DIR"/generate_tarball.sh "$NAME" "$OS"
echo "Unpacking tarball: $NAME.tar.gz..."
tar -xzvf "$DIR"/"$NAME".tar.gz -C "$PROJECT"
dpkg-deb --build "$PROJECT"
mv "$PROJECT".deb "$NAME".deb  # rename DUNE.deb to antelopeio-dune<etc>.deb
mv "$NAME".* "$ORIGINAL_DIR"   # move into user's original path
rm -r "$PROJECT"

exit 0
