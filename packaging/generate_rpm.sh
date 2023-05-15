#! /bin/bash -e

PREFIX="usr"
SPREFIX=${PREFIX}
SUBPREFIX="opt/${PROJECT}/${VERSION}"
SSUBPREFIX="opt\/${PROJECT}\/${VERSION}"
RELEASE="${VERSION_SUFFIX}"

# default release to "1" if there is no suffix
if [[ -z $RELEASE ]]; then
  RELEASE="1"
fi

PROJECT="$PROJECT"
NAME="${PROJECT}-${VERSION_NO_SUFFIX}-${RELEASE}"

export PREFIX
export SUBPREFIX
export SPREFIX
export SSUBPREFIX

. ./generate_tarball.sh "$NAME"

RPMDIR="$HOME/rpmbuild/BUILDROOT/$NAME.x86_64"
mkdir -p "$RPMDIR"
RPMBUILD=$(realpath "$RPMDIR")
FILES=$(tar -xvzf "$NAME".tar.gz -C "$RPMBUILD")
PFILES=""
for f in $FILES; do
  if [ -L "$RPMBUILD"/"$f" ] || [ -f "$RPMBUILD"/"$f" ]; then
    PFILES="${PFILES}/${f}\n"
  fi
done
mkdir -p "$HOME"/rpmbuild/BUILD
echo -e "$PFILES" &> "$HOME"/rpmbuild/BUILD/filenames.txt

mkdir -p "$PROJECT"
echo -e "Name: ${PROJECT} 
Version: ${VERSION_NO_SUFFIX}
License: MIT
Vendor: ${VENDOR} 
Source: ${URL} 
URL: ${URL} 
Packager: ${VENDOR} <${EMAIL}>
Summary: ${DESC}
Release: ${RELEASE}
Requires: python3, (docker or docker-ce-cli), curl, wget
%description
${DESC}
%files -f filenames.txt" &> "$PROJECT".spec
cat "$PROJECT".spec

rpmbuild -bb "$PROJECT".spec
mv "$HOME"/rpmbuild/RPMS/x86_64/*.rpm "$ORIGINAL_DIR"  

rm -r "$PROJECT" "$HOME"/rpmbuild/BUILD/filenames.txt "$PROJECT".spec
