#!/usr/bin/env python3

"""Test DUNE args remainder

This script tests if there is a warning if user passes
unused arguments to DUNE
"""

import subprocess

from common import DUNE_EXE
from container import container


def test_unused():
    """Test the warning for unused arguments"""

    # Remove any container that already exists.
    cntr = container('dune_container', 'dune:latest')
    if cntr.exists():
        subprocess.run([DUNE_EXE, "--destroy-container"], check=True)

    # List of expected values.
    expect_list = \
        [
            b"Warning: following arguments were possibly unused: ['config.ini']",
        ]

    # Call DUNE with improper arguments
    completed_process = subprocess.run([DUNE_EXE,"--start", "my_node", "config.ini"], check=True, stdout=subprocess.PIPE)

    # Test for expected values in the captured output.
    for expect in expect_list:
        assert expect in completed_process.stdout

def test_no_warning():
    """Test there is no warning for arguments using remainder in i.e. gdb case"""

    # List of expected values.
    unexpected_list = \
        [
            b'Warning: following arguments were possibly unused:',
        ]

    # Call DUNE.
    completed_process = subprocess.run([DUNE_EXE,"--gdb", "/usr/bin/echo", "Hello"], check=True, stdout=subprocess.PIPE)

    # Test values are NOT in the captured output.
    for unexpected in unexpected_list:
        assert unexpected not in completed_process.stdout
