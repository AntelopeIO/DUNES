#!/usr/bin/env python3

"""Test image bootstrap with various versions of CDT, leap, and reference-contracts.

This script tests that the bootstrap command can create an image with a given version or versions.

This test contains resource intense tests that should NOT be run on every commit.
To enable during testing, add `--run-slow` to your pytest command.
"""

import sys
import subprocess
import os
import pytest

from common import DUNES_ROOT


TAG_PREFIX = 'dunes:'
CONTAINER_NAME_PREFIX = 'dt_'


def sub_versions(name, cdt=None, leap=None, contracts=None):
    """Tests that versions are set."""

    # Set up some constants.
    container_name = f'{CONTAINER_NAME_PREFIX}{name}'
    image_tag = f'{TAG_PREFIX}{name}'
    bootstrap_command = [sys.executable, os.path.join(DUNES_ROOT, "bootstrap.py"), f'--tag={image_tag}']

    # Clean any existing images/containers.
    # Send output to subprocess.DEVNULL since we EXPECT docker to tell us containers and images don't exist.
    #   pylint: disable=subprocess-run-check, line-too-long
    subprocess.run(['docker', 'container', 'stop', container_name, '--force'], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL, check=False)
    subprocess.run(['docker', 'container', 'rm', container_name, '--force'], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL, check=False)
    subprocess.run(['docker', 'image', 'rm', image_tag], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL, check=False)

    # Add versions:
    if cdt:
        bootstrap_command.append(f'--cdt={cdt}')
    if leap:
        bootstrap_command.append(f'--leap={leap}')
    if contracts:
        bootstrap_command.append(f'--contracts={contracts}')

    # Execute the bootstrap function.
    subprocess.run(bootstrap_command, check=True)

    # Start the container
    subprocess.run(['docker', 'create', '-it', '--name', container_name, image_tag, '/bin/bash'], check=True)
    subprocess.run(['docker', 'start', container_name], check=True)

    # Test the versions are in the started container.
    if cdt:
        # Try to get CDT version info from inside the container and test it matches.
        #  pylint: disable=line-too-long
        completed_process = subprocess.run(['docker', 'exec', '-i', container_name, '/usr/bin/ls', '/usr/opt/cdt'], check=False, stdout=subprocess.PIPE)
        assert cdt in completed_process.stdout.decode()
    if leap:
        # Try to get LEAP version info from inside the container and test it matches.
        #  pylint: disable=line-too-long
        completed_process = subprocess.run(['docker', 'exec', '-i', container_name, 'leap-util', 'version', 'client'], check=False, stdout=subprocess.PIPE)
        assert leap in completed_process.stdout.decode()
    if contracts:
        # Try to get contracts version info from inside the container and test it matches.
        #  pylint: disable=line-too-long
        completed_process = subprocess.run(['docker', 'exec', '-i', container_name, 'cat', '/app/reference-contracts/VERSION.DUNES.txt'], check=False, stdout=subprocess.PIPE)
        assert contracts in completed_process.stdout.decode()

    # Stop the container, remove it, and remove the image.
    subprocess.run(['docker', 'container', 'stop', container_name], check=True)
    subprocess.run(['docker', 'container', 'rm', container_name], check=True)
    subprocess.run(['docker', 'image', 'rm', image_tag], check=True)


# ONLY this test is NOT marked slow. And only because we want it to run ALWAYS.
@pytest.mark.safe
def test_combo1():
    """Ensure bootstrap can create an image with given CDT and LEAP versions."""
    sub_versions('dunes_for_ci', cdt='3.0.1', leap='3.2.1', contracts='2ae64b0b9a9096a3d25339c3df364e08fde66258')


@pytest.mark.slow
@pytest.mark.safe
def test_combo2():
    sub_versions('dunes_for_ci', cdt='3.1.0', leap='4.0.0')

@pytest.mark.slow
@pytest.mark.safe
def test_cdt1():
    sub_versions('cdt1', cdt='3.0.1')

@pytest.mark.slow
@pytest.mark.safe
def test_cdt2():
    sub_versions('cdt2', cdt='3.1.0')

@pytest.mark.slow
@pytest.mark.safe
def test_leap1():
    sub_versions('leap1', leap='3.2.3')

@pytest.mark.slow
@pytest.mark.safe
def test_leap2():
    sub_versions('leap2', leap='3.2.2')

@pytest.mark.slow
@pytest.mark.safe
def test_contracts1():
    sub_versions('contracts1', contracts='bd6c0b1a5086c8826a2840e7b8b5e1adaff00314')

@pytest.mark.slow
@pytest.mark.safe
def test_contracts2():
    sub_versions('contracts1', cdt='3.1.0', contracts='2ae64b0b9a9096a3d25339c3df364e08fde66258')


if __name__ == "__main__":
    test_combo1()
    test_combo2()
    test_cdt1()
    test_cdt2()
    test_leap1()
    test_leap2()
    test_contracts1()
    test_contracts2()
