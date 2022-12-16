#!/usr/bin/env python3

"""Test DUNE Version_

This script tests that the compiled binary produce expected output
in response to `--version` option.
"""



import subprocess

from common import DUNE_EXE


def test_version():
    """Test that the output of `--version` is as expected."""

    # List of expected values.
    expect_list = \
        [
            b'DUNE v1.',
        ]

    # Call DUNE.
    completed_process = subprocess.run([DUNE_EXE,"--version"], check=True, stdout=subprocess.PIPE)

    # Test for expected values in the captured output.
    for expect in expect_list:
        assert expect in completed_process.stdout
