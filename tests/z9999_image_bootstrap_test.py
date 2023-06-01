#!/usr/bin/env python3

"""Bootstrap CDT Version Test

This script tests that the bootstrap command can create an image with a given version.
"""

import sys
import subprocess
import os

from common import DUNES_ROOT


#CONTAINER_NAME='dunes_version_test'
#IMAGE_TAG='dunes:dunes_version_test'

TAG_PREFIX = 'dunes:'
CONTAINER_NAME_PREFIX = 'dt_'

# List of all possible names sent to subprocess. Used in cleanup().
CLEANUP_NAMES = [
    'dunes_for_ci',
    'cdt1', 'cdt2',
    'leap1', 'leap2',
    'combo1', 'combo2'
]


def cleanup():
    """Remove any existing test containers and images."""

    for name in CLEANUP_NAMES:
        # Set up some constants.
        CONTAINER_NAME = f'{CONTAINER_NAME_PREFIX}{name}'
        IMAGE_TAG = f'{TAG_PREFIX}{name}'

        # Send output to subprocess.DEVNULL since we EXPECT docker to tell us containers and images don't exist.
        #   pylint: disable=subprocess-run-check
        subprocess.run(['docker', 'container', 'rm', CONTAINER_NAME, '--force'], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL, check=False)
        #   pylint: disable=subprocess-run-check
        subprocess.run(['docker','image','rm',IMAGE_TAG], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL, check=False)


def sub_versions(name, cdt=None, leap=None, refcon=None):
    """Tests that versions are set."""

    # Sanity check and cleanup assurance.
    assert name is not None
    assert name in CLEANUP_NAMES, f"TEST DEFECT: name ({name}) is missing from CLEAN_NAMES array."

    # Set up some constants.
    CONTAINER_NAME = f'{CONTAINER_NAME_PREFIX}{name}'
    IMAGE_TAG = f'{TAG_PREFIX}{name}'

    bootstrap_command = [sys.executable, os.path.join(DUNES_ROOT, "bootstrap.py"), f'--tag={IMAGE_TAG}']

    # Add versions:
    if cdt:
        bootstrap_command.append(f'--cdt={cdt}')
    if leap:
        bootstrap_command.append(f'--leap={leap}')
    if refcon:
        bootstrap_command.append(f'--refcon={refcon}')

    # Execute the bootstrap function.
    subprocess.run(bootstrap_command, check=True)

    # Start the container
    subprocess.run(['docker', 'create', '-it', '--name', CONTAINER_NAME, IMAGE_TAG, '/bin/bash'], check=True)
    subprocess.run(['docker', 'start', CONTAINER_NAME], check=True)

    if cdt:
        # Try to get CDT version info from inside the container and test it matches.
        completed_process = subprocess.run(['docker', 'exec', '-i', CONTAINER_NAME, '/usr/bin/ls', '/usr/opt/cdt'], check=False, stdout=subprocess.PIPE)
        assert cdt in completed_process.stdout.decode()


    if leap:
        # Try to get LEAP version info from inside the container and test it matches.
        completed_process = subprocess.run(['docker', 'exec', '-i', CONTAINER_NAME, 'leap-util', 'version', 'client'], check=False, stdout=subprocess.PIPE)
        assert leap in completed_process.stdout.decode()

    if refcon:
        # Try to get refcon version info from inside the container and test it matches.
        completed_process = subprocess.run(['docker', 'exec', '-i', CONTAINER_NAME, 'leap-util', 'version', 'client'], check=False, stdout=subprocess.PIPE)
        assert refcon in completed_process.stdout.decode()




def test_simple_version():
    """Ensure bootsrap can be created with given CDT and LEAP versions."""

    # Start in a clean state.
    cleanup()

    # Call the test with specific cdt and leap versions.
    sub_versions('dunes_for_ci', cdt='3.0.1', leap='3.2.1')

    # End in a clean state.
    cleanup()


def test_cdt_leap_versions_non_ci():
    """
    Ensure bootsrap can be created with given CDT and LEAP versions.
    This is intended to be run locally and not on github CI.
    To diable from ci, add `-k "not non_ci"` to your pytest command (e.g. `pytest -k "not non_ci" tests`)
    """

    # Start in a clean state.
    cleanup()

    # Look at the version updates one at a time.
    sub_versions('cdt1', cdt='3.0.1')
    sub_versions('cdt2', cdt='3.1.0')
    sub_versions('leap1', leap='3.2.3')
    sub_versions('leap2', leap='3.2.2')
    #sub_versions('t3', refcon='git-commit-hash-goes-here')

    sub_versions('combo1', cdt='3.0.1', leap='3.2.1')
    sub_versions('combo2', cdt='3.1.0', leap='3.2.3')


    # End in a clean state.
    cleanup()


if __name__ == "__main__":
    test_simple_version()
    test_cdt_leap_versions_non_ci()
