#!/bin/sh

# This file MUST remain co-located with the files to work.


# Find paths to the tests and the dune executable.
SCRIPT=`readlink -f "$0"`
TEST_DIR=`dirname "$SCRIPT"`
DUNE_DIR=`dirname "$TEST_DIR"`
DUNE="$DUNE_DIR/dune"

# Get a list of the options.
options=`$DUNE --help | grep -o "^  --[a-z\-]*"`

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
