#!/usr/bin/env python3

"""Test DUNE container controls

This script test works with the Docker container.
"""
import subprocess

from common import DUNE_EXE
from container import container


def test_container_actions():
    """ Test the start, stop, and destroy action for containers. """

    cntr = container('dune_container', 'dune:latest')

    # Remove any container that already exists.
    if cntr.exists():
        subprocess.run([DUNE_EXE, "--destroy-container"], check=True)

    # Create/start the container.
    subprocess.run([DUNE_EXE, "--start-container"], check=True)
    assert cntr.check_status("running") is True

    # Stop the container.
    subprocess.run([DUNE_EXE, "--stop-container"], check=True)
    assert cntr.check_status("exited") is True

    # Restart the container.
    subprocess.run([DUNE_EXE, "--start-container"], check=True)
    assert cntr.check_status("running") is True

    # Destroy the container.
    subprocess.run([DUNE_EXE, "--destroy-container"], check=True)
    assert cntr.exists() is False
