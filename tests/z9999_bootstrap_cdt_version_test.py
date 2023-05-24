#!/usr/bin/env python3

"""Bootstrap CDT Version Test

This script tests that the bootstrap command can create an image with a given version.
"""


import subprocess
import os

from common import TEST_PATH


CONTAINER_NAME='dunes_version_test'
IMAGE_TAG='dunes_version_test'
IMAGE_NAME='dunes:dunes_version_test'

BOOTSTRAP=os.path.join( os.path.split(TEST_PATH)[0] , "bootstrap.sh")
CDT_VERSION='3.0.1'
LEAP_VERSION='3.2.1'


def cleanup():
    """Remove any existing test containers and images."""

    #   pylint: disable=subprocess-run-check
    subprocess.run(['docker', 'container', 'rm', CONTAINER_NAME, '--force'], check=False)
    #   pylint: disable=subprocess-run-check
    subprocess.run(['docker','image','rm',IMAGE_NAME], check=False)


def test_version_bootstrapping():
    """Ensure bootsrap can be created with a given CDT version."""

    # Start in a clean state.
    cleanup()

    # Execute the bootstrap function.
    subprocess.run([BOOTSTRAP, '--cdt='+CDT_VERSION, '--leap='+LEAP_VERSION, '--tag='+IMAGE_TAG], check=True)

    # Start the container
    subprocess.run(['docker', 'create', '-it', '--name', CONTAINER_NAME, IMAGE_NAME, '/bin/bash'], check=True)
    subprocess.run(['docker', 'start', CONTAINER_NAME], check=True)

    # Try to get CDT version info from inside the container.
    completed_process = subprocess.run(['docker', 'exec', '-i', CONTAINER_NAME, '/usr/bin/ls', '/usr/opt/cdt'],
                                       check=False, stdout=subprocess.PIPE)
    # Test that the version is in the output.
    assert CDT_VERSION in completed_process.stdout.decode()

    # Try to get LEAP version info from inside the container.
    completed_process = subprocess.run(['docker', 'exec', '-i', CONTAINER_NAME, 'leap-util', 'version', 'client'],
                                       check=False, stdout=subprocess.PIPE)
    # Test that the version is in the output.
    assert LEAP_VERSION in completed_process.stdout.decode()

    # End in a clean state.
    cleanup()


if __name__ == "__main__":
    test_version_bootstrapping()
