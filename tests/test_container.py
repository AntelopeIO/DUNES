#!/usr/bin/env python3

"""Test DUNES container controls

This script test works with the Docker container.
"""
import subprocess
import pytest

from common import DUNES_EXE, TEST_CONTAINER_NAME, TEST_IMAGE_NAME, stop_dunes_containers
from container import container


@pytest.mark.safe
def test_init():
    stop_dunes_containers()


@pytest.mark.safe
def test_container_actions():
    """ Test the start, stop, and destroy action for containers. """

    cntr = container(TEST_CONTAINER_NAME, TEST_IMAGE_NAME)

    # Remove any container that already exists.
    if cntr.exists():
        subprocess.run([DUNES_EXE, '-C', TEST_CONTAINER_NAME, "--destroy-container"], check=True)

    # Create/start the container.
    subprocess.run([DUNES_EXE, '-C', TEST_CONTAINER_NAME, "--start-container"], check=True)
    assert cntr.check_status("running") is True

    # Stop the container.
    subprocess.run([DUNES_EXE, '-C', TEST_CONTAINER_NAME, "--stop-container"], check=True)
    assert cntr.check_status("exited") is True

    # Restart the container.
    subprocess.run([DUNES_EXE, '-C', TEST_CONTAINER_NAME, "--start-container"], check=True)
    assert cntr.check_status("running") is True

    # Destroy the container.
    subprocess.run([DUNES_EXE, '-C', TEST_CONTAINER_NAME, "--destroy-container"], check=True)
    assert cntr.exists() is False
