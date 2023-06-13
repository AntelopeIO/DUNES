#!/usr/bin/env python3

"""Test in place verrsion changes for leap, CDT, and reference-contracts.

   Note that not all version of CDT and all versions of leap and all
   versions of contracts work together. So the order tests are called
   in is important.
"""

import subprocess
import pytest

from common import DUNES_EXE


def switch_versions_call(cdt, leap, contracts):
    """Build the version update command."""

    if cdt:
        subprocess.run( [DUNES_EXE,'--cdt',cdt], check=True)
    if leap:
        subprocess.run( [DUNES_EXE,'--leap',leap], check=True)
    if contracts:
        subprocess.run( [DUNES_EXE,'--contracts',contracts], check=True)


def switch_versions(cdt=None, leap=None, contracts=None):
    """Tests that versions are set."""

    switch_versions_call(cdt, leap, contracts)

    container_name = 'dunes_container'

    # Test the versions are in the container.
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


@pytest.mark.destructive
def test_begin():
    # Start a container.
    subprocess.run([DUNES_EXE, "--start-container"], check=True)


@pytest.mark.destructive
def test_combo1():
    switch_versions(cdt='3.0.1', leap='3.2.1', contracts='2ae64b0b9a9096a3d25339c3df364e08fde66258')

@pytest.mark.destructive
def test_combo2():
    switch_versions(cdt='3.1.0', leap='4.0.0', contracts='bd6c0b1a5086c8826a2840e7b8b5e1adaff00314')

@pytest.mark.destructive
def test_leap1():
    switch_versions(leap='3.2.1')

@pytest.mark.destructive
def test_cdt1():
    switch_versions(cdt='3.0.1')

@pytest.mark.destructive
def test_contracts1():
    switch_versions(contracts='2ae64b0b9a9096a3d25339c3df364e08fde66258')


@pytest.mark.destructive
def test_end():
    # Just call with the latest.
    switch_versions_call("latest", "latest", "latest")



if __name__ == "__main__":
    test_begin()
    test_combo1()
    test_combo2()
    test_leap1()
    test_cdt1()
    test_contracts1()
    test_end()
