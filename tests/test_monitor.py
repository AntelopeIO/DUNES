#!/usr/bin/env python3

"""Test DUNES Version

This script tests --monitor key

"""
import subprocess
import pytest

from common import DUNES_EXE, TEST_CONTAINER_NAME, TEST_IMAGE_NAME, stop_dunes_containers, destroy_test_container
from container import container


@pytest.mark.safe
def test_init():
    stop_dunes_containers()
    destroy_test_container()

@pytest.mark.safe
def test_monitor():
    """Test `--monitor` key."""

    # Remove any container that already exists.
    cntr = container(TEST_CONTAINER_NAME, TEST_IMAGE_NAME)
    if cntr.exists():
        subprocess.run([DUNES_EXE, '-C', TEST_CONTAINER_NAME, "--destroy-container"], check=True)

    # This will start a container; however, there will be NO active node, so it will fail.
    results = subprocess.run([DUNES_EXE, '-C', TEST_CONTAINER_NAME, "--monitor"], capture_output=True, check=False)
    assert results.returncode != 0
    assert cntr.check_status("running") is True

    # Start a node.
    subprocess.run([DUNES_EXE, '-C', TEST_CONTAINER_NAME, "--start", "my_node"], check=True)

    # Now try to monitor again.
    results = subprocess.run([DUNES_EXE, '-C', TEST_CONTAINER_NAME, "--monitor"], capture_output=True, check=False)
    assert b'server_version' in results.stdout
