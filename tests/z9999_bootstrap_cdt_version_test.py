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

def cleanup():
    """Remove any existing test containers and images."""

    #   pylint: disable=subprocess-run-check
    subprocess.run(['docker','container','rm',CONTAINER_NAME], check=False)
    #   pylint: disable=subprocess-run-check
    subprocess.run(['docker','image','rm',IMAGE_NAME], check=False)


def test_version_bootstrapping():
    """Ensure bootsrap can be created with a given CDT version."""

    # Start in a clean state.
    cleanup()

    # Execute the bootstrap function.
    subprocess.run([BOOTSTRAP, '--cdt='+CDT_VERSION, '--tag='+IMAGE_TAG], check=True)

    # Try to get CDT version info from iside the container.
    completed_process = subprocess.run(['docker', 'run', '--name', CONTAINER_NAME, '-it', IMAGE_NAME, '/usr/bin/ls', '/usr/opt/cdt'],
                                       check=False, stdout=subprocess.PIPE)
    # Test that the version is in the output.
    assert CDT_VERSION in completed_process.stdout.decode()

    # End in a clean state.
    cleanup()


if __name__ == "__main__":
    test_version_bootstrapping()
