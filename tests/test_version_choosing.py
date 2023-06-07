#!/usr/bin/env python3

"""Test DUNES cdt and leap version choosing
"""


import subprocess
import pytest

from common import DUNES_EXE


@pytest.mark.safe
def test_version_choosing():

    # Both --leap and --cdt should have at least 3 last versions
    expect_list = \
        [
            b'1) v',
            b'2) v',
            b'3) v',
        ]

    # Ignore checking return code, because eventually we don't choose any version
    completed_process = subprocess.run([DUNES_EXE, "--leap"], check=False, stdout=subprocess.PIPE)

    # Test for expected values in the captured output.
    for expect in expect_list:
        assert expect in completed_process.stdout

    # Ignore checking return code, because eventually we don't choose any version
    completed_process = subprocess.run([DUNES_EXE, "--cdt"], check=False, stdout=subprocess.PIPE)

    # Test for expected values in the captured output.
    for expect in expect_list:
        assert expect in completed_process.stdout
