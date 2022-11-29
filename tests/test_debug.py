#!/usr/bin/env python3

"""Test DUNE Version

This script tests that the compiled binary produces output in response
to `--debug` option.

"""



import subprocess

from common import DUNE_EXE


def test_version_debug():
    """Test that the output of `--version --debug` is as expected."""

    # Call DUNE, we only care that `--debug` is available, not that it
    # does anything. For now.
    completed_process = subprocess.run([DUNE_EXE,"--version","--debug"], check=True)
