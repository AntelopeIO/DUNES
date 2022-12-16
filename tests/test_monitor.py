#!/usr/bin/env python3

"""Test DUNE Version

This script tests --monitor key

"""
import subprocess

from common import DUNE_EXE
from container import container


def test_monitor():
    """Test `--monitor` key."""


    # Remove any container that already exists.
    cntr = container('dune_container', 'dune:latest')
    if cntr.exists():
        subprocess.run([DUNE_EXE, "--destroy-container"], check=True)

    # This will start a container; however, there will be NO active node, so it will fail.
    results = subprocess.run([DUNE_EXE, "--monitor"], capture_output=True, check=False)
    assert results.returncode != 0
    assert cntr.check_status("running") is True

    # Start a node.
    subprocess.run([DUNE_EXE,"--start", "my_node"], check=True)

    # Now try to monitor again.
    results = subprocess.run([DUNE_EXE, "--monitor"], capture_output=True, check=False)
    assert b'server_version' in results.stdout
