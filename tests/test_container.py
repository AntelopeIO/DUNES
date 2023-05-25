#!/usr/bin/env python3

"""Test DUNES container controls

This script test works with the Docker container.
"""
import subprocess

from common import DUNES_EXE
from container import container


def test_container_actions():
    """ Test the start, stop, and destroy action for containers. """

    cntr = container('dunes_container', 'dunes:latest')

    # Remove any container that already exists.
    if cntr.exists():
        subprocess.run([DUNES_EXE, "--destroy-container"], check=True)

    # Create/start the container.
    subprocess.run([DUNES_EXE, "--start-container"], check=True)
    assert cntr.check_status("running") is True

    # Stop the container.
    subprocess.run([DUNES_EXE, "--stop-container"], check=True)
    assert cntr.check_status("exited") is True

    # Restart the container.
    subprocess.run([DUNES_EXE, "--start-container"], check=True)
    assert cntr.check_status("running") is True

    # Destroy the container.
    subprocess.run([DUNES_EXE, "--destroy-container"], check=True)
    assert cntr.exists() is False
