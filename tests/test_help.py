#!/usr/bin/env python3

"""Test DUNES Help

This script tests that the compiled binary produce expected output
in response to `-h`, `--help`, and `<some invalid option>` options.
"""

import subprocess
import pytest

from common import DUNES_EXE


@pytest.mark.safe
def test_invalid_option():
    """Test that the output of `dunes <some invalid option>` is as expected."""

    # List of expected values.
    expect_list = \
        [
            b'usage: dunes',
            b'dunes: error: unrecognized arguments: --some-invalid-option'
        ]

    # Call the tool, check for failed return code
    # pylint: disable=subprocess-run-check
    completed_process = subprocess.run([DUNES_EXE, "--some-invalid-option"], stderr=subprocess.PIPE)
    assert completed_process.returncode != 0

    # Test for expected values in the captured output.
    for expect in expect_list:
        assert expect in completed_process.stderr


@pytest.mark.safe
def test_help():
    """Test that the output of `dunes -h` and `dunes --help` is as expected."""

    # List of expected values.
    expect_list = \
        [
            b'usage: dunes',
            b'DUNES: Docker Utilities for Node Execution',
            b'-h, --help',
            b'--monitor',
            b'--start',
            b'--stop',
            b'--remove',
            b'--list',
            b'--version',
        ]


    # Call DUNES.
    completed_process_h = subprocess.run([DUNES_EXE, "-h"], check=True, stdout=subprocess.PIPE)

    # Call DUNES.
    completed_process_help = subprocess.run([DUNES_EXE, "--help"], check=True, stdout=subprocess.PIPE)

    # Test that the output of all the above executions is the same
    assert completed_process_h.stdout == completed_process_help.stdout

    # Test for expected values in the captured output.
    #  We need only test ONE output because we ensure the output is the same above.
    for expect in expect_list:
        assert expect in completed_process_h.stdout
