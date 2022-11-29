#!/usr/bin/env python3

"""Test DUNE Version_

This script tests that the compiled binary produce expected output
in response to `--version` option.
"""



import subprocess

from common import TEST_PATH


def test_all_options_tested():
    """Test that all the options from the output of `--help` are in the various test files."""

    script=TEST_PATH+"/show_untested_options.sh"

    completed_process = subprocess.run(script, check=True)
