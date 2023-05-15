#!/bin/sh

# This file MUST remain co-located with the files to work.


# Find paths to the tests and the DUNES executable.
SCRIPT=`readlink -f "$0"`
TEST_DIR=`dirname "$SCRIPT"`
DUNES_DIR=`dirname "$TEST_DIR"`
DUNES="$DUNES_DIR/dunes"

# Get a list of the options.
options=`$DUNES --help | grep -o "^  --[a-z\-]*"`

# Get a list of the test files.
files=`find "$TEST_DIR" | grep "[.]py\$"`

# Return value. Initially set to zero/success.
rv=0

# Search for each option.
for opt in $options; do
    if ! grep --quiet \"$opt\" $files ; then
        # Report missing options and set the return value to non-zeor/failure.
        echo "Missing option: $opt"
        rv=1
    fi
done

# Report success/fail.
exit $rv
