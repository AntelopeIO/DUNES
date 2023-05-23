#!/usr/bin/env python3

"""Test DUNES Version

This script tests that the compiled binary produces output in response
to `--debug` option.

"""


import subprocess

from common import DUNES_EXE


def test_version_debug():
    """Test that the output of `--version --debug` is as expected."""

    # Call DUNES, we only care that `--debug` is available, not that it
    # does anything. For now.
    subprocess.run([DUNES_EXE, "--version", "--debug"], check=True)
