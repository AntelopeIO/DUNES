#!/usr/bin/env python3

"""Test DUNES Version_

This script tests that the compiled binary produce expected output
in response to `--version` option.
"""


import subprocess
import pytest

from common import DUNES_EXE


@pytest.mark.safe
def test_version():
    """Test that the output of `--version` is as expected."""

    # List of expected values.
    expect_list = \
        [
            b'DUNES v1.',
        ]

    # Call DUNES.
    completed_process = subprocess.run([DUNES_EXE, "--version"], check=True, stdout=subprocess.PIPE)

    # Test for expected values in the captured output.
    for expect in expect_list:
        assert expect in completed_process.stdout
