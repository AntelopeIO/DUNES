#!/usr/bin/env python3

"""Test DUNES args remainder

This script tests if there is a warning if user passes
unused arguments to DUNES
"""

import subprocess
import pytest

from common import DUNES_EXE
from container import container


@pytest.mark.safe
def test_unused():
    """Test the warning for unused arguments"""

    # Remove any container that already exists.
    cntr = container('dunes_container', 'dunes:latest')
    if cntr.exists():
        subprocess.run([DUNES_EXE, "--destroy-container"], check=True)

    # List of expected values.
    expect_list = \
        [
            b"Warning: following arguments were possibly unused: ['config.ini']",
        ]

    # Call DUNES with improper arguments
    completed_process = subprocess.run([DUNES_EXE, "--start", "my_node", "config.ini"],
                                       check=True, stdout=subprocess.PIPE)

    # Test for expected values in the captured output.
    for expect in expect_list:
        assert expect in completed_process.stdout


@pytest.mark.safe
def test_no_warning():
    """Test there is no warning for arguments using remainder in i.e. gdb case"""

    # List of expected values.
    unexpected_list = \
        [
            b'Warning: following arguments were possibly unused:',
        ]

    # Call DUNES.
    completed_process = subprocess.run([DUNES_EXE, "--gdb", "/usr/bin/echo", "Hello"],
                                       check=True, stdout=subprocess.PIPE)

    # Test values are NOT in the captured output.
    for unexpected in unexpected_list:
        assert unexpected not in completed_process.stdout
