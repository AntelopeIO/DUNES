#!/usr/bin/env python3

"""Test in place verrsion changes for leap, CDT, and reference-contracts.

   Note that not all version of CDT and all versions of leap and all
   versions of contracts work together. So the order tests are called
   in is important.
"""

import subprocess
import pytest

from common import DUNES_EXE, TEST_CONTAINER_NAME, stop_dunes_containers, destroy_test_container


@pytest.mark.safe
def test_init():
    stop_dunes_containers()


def switch_versions_call(cdt, leap, contracts):
    """Build the version update command."""

    if cdt:
        subprocess.run( [DUNES_EXE, '-C', TEST_CONTAINER_NAME, '--cdt', cdt], check=True)
    if leap:
        subprocess.run( [DUNES_EXE, '-C', TEST_CONTAINER_NAME, '--leap', leap], check=True)
    if contracts:
        subprocess.run( [DUNES_EXE, '-C', TEST_CONTAINER_NAME, '--contracts', contracts], check=True)


def switch_versions(cdt=None, leap=None, contracts=None):
    """Tests that versions are set."""

    switch_versions_call(cdt, leap, contracts)

    # Test the versions are in the container.
    if cdt:
        # Try to get CDT version info from inside the container and test it matches.
        #  pylint: disable=line-too-long
        completed_process = subprocess.run(['docker', 'exec', '-i', TEST_CONTAINER_NAME, '/usr/bin/ls', '/usr/opt/cdt'], check=False, stdout=subprocess.PIPE)
        assert cdt in completed_process.stdout.decode()
    if leap:
        # Try to get LEAP version info from inside the container and test it matches.
        #  pylint: disable=line-too-long
        completed_process = subprocess.run(['docker', 'exec', '-i', TEST_CONTAINER_NAME, 'leap-util', 'version', 'client'], check=False, stdout=subprocess.PIPE)
        assert leap in completed_process.stdout.decode()
    if contracts:
        # Try to get contracts version info from inside the container and test it matches.
        #  pylint: disable=line-too-long
        completed_process = subprocess.run(['docker', 'exec', '-i', TEST_CONTAINER_NAME, 'cat', '/app/reference-contracts/VERSION.DUNES.txt'], check=False, stdout=subprocess.PIPE)
        assert contracts in completed_process.stdout.decode()


@pytest.mark.safe
def test_begin():
    # Start a test container.
    subprocess.run([DUNES_EXE, '-C', TEST_CONTAINER_NAME, "--start-container"], check=True)


@pytest.mark.safe
def test_combo1():
    switch_versions(cdt='3.0.1', leap='3.2.1', contracts='2ae64b0b9a9096a3d25339c3df364e08fde66258')

@pytest.mark.safe
def test_combo2():
    switch_versions(cdt='3.1.0', leap='4.0.0', contracts='bd6c0b1a5086c8826a2840e7b8b5e1adaff00314')

@pytest.mark.safe
def test_leap1():
    switch_versions(leap='3.2.1')

@pytest.mark.safe
def test_cdt1():
    switch_versions(cdt='3.0.1')

@pytest.mark.safe
def test_contracts1():
    switch_versions(contracts='2ae64b0b9a9096a3d25339c3df364e08fde66258')


@pytest.mark.safe
def test_end():
    destroy_test_container()


if __name__ == "__main__":
    test_begin()
    test_combo1()
    test_combo2()
    test_leap1()
    test_cdt1()
    test_contracts1()
