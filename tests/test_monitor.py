#!/usr/bin/env python3

"""Test DUNES Version

This script tests --monitor key

"""
import subprocess
import pytest

from common import DUNES_EXE
from container import container


@pytest.mark.destructive
def test_monitor():
    """Test `--monitor` key."""

    # Remove any container that already exists.
    cntr = container('dunes_container', 'dunes:latest')
    if cntr.exists():
        subprocess.run([DUNES_EXE, "--destroy-container"], check=True)

    # This will start a container; however, there will be NO active node, so it will fail.
    results = subprocess.run([DUNES_EXE, "--monitor"], capture_output=True, check=False)
    assert results.returncode != 0
    assert cntr.check_status("running") is True

    # Start a node.
    subprocess.run([DUNES_EXE, "--start", "my_node"], check=True)

    # Now try to monitor again.
    results = subprocess.run([DUNES_EXE, "--monitor"], capture_output=True, check=False)
    assert b'server_version' in results.stdout
