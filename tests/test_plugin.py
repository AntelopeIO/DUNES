#!/usr/bin/env python3

"""Test DUNES Plugin

This script tests that after copying plugin to src/plugin DUNES detects it and run properly.
"""

import os
import shutil
import subprocess
import pytest

from common import DUNES_EXE, DUNES_ROOT, TEST_PATH, stop_dunes_containers


src_hello  = os.path.join(DUNES_ROOT, *['plugin_example', 'dunes_hello'])
src_gotcha = os.path.join(TEST_PATH, 'gotcha')

PLUGIN_DIR = os.path.join(DUNES_ROOT, *['src','plugin'])
dst_hello  = os.path.join(PLUGIN_DIR, 'dunes_hello')
dst_fail   = os.path.join(PLUGIN_DIR, 'dunes_fail')
dst_gotcha = os.path.join(PLUGIN_DIR, 'gotcha')



@pytest.mark.safe
def test_init():
    stop_dunes_containers()


def remove_all():
    """Remove all the test plugins"""
    shutil.rmtree(dst_hello, ignore_errors=True)
    shutil.rmtree(dst_fail, ignore_errors=True)
    shutil.rmtree(dst_gotcha, ignore_errors=True)


@pytest.mark.safe
def test_hello():
    """Test the working hello plugin."""

    # Clean then copy.
    remove_all()
    shutil.copytree(src_hello, dst_hello)

    # Call DUNES with '--help' flag and test for the expected result.
    completed_process = subprocess.run([DUNES_EXE, "--help"], check=True, stdout=subprocess.PIPE)
    assert '--hello' in completed_process.stdout.decode()

    # Call DUNES with '--hello' flag and test for the expected result.
    completed_process = subprocess.run([DUNES_EXE, "--hello"], check=True, stdout=subprocess.PIPE)
    assert 'Hello from DUNES' in completed_process.stdout.decode()

    # Cleanup.
    remove_all()


@pytest.mark.safe
def test_fail():
    """Test that a duplicate working hello plugin."""

    # Clean then copy. Note that the fail plugin is a simple duplicate of hello.
    remove_all()
    shutil.copytree(src_hello, dst_hello)
    shutil.copytree(src_hello, dst_fail)

    # Call DUNES with '--help' flag and test for the expected result.
    completed_process = subprocess.run([DUNES_EXE, "--help"], check=True, stdout=subprocess.PIPE)
    assert '--hello' in completed_process.stdout.decode()
    assert "Can't load module <" in completed_process.stdout.decode()

    # Call DUNES with '--hello' flag and test for the expected result.
    completed_process = subprocess.run([DUNES_EXE, "--hello"], check=True, stdout=subprocess.PIPE)
    assert 'Hello from DUNES' in completed_process.stdout.decode()
    assert "Can't load module <" in completed_process.stdout.decode()

    # Cleanup.
    remove_all()


@pytest.mark.safe
def test_missing_main():
    """Test that a directory missing a main.py file."""

    # Clean up then make the empty directory.
    remove_all()
    os.mkdir(dst_gotcha)

    # Call DUNES with '--help' flag and test for the expected result.
    completed_process = subprocess.run([DUNES_EXE, "--help"], check=True, stdout=subprocess.PIPE)
    assert 'main.py not found in' in completed_process.stdout.decode()

    remove_all()


@pytest.mark.safe
def test_gotcha():
    """Test a bad plugin generates a notification."""

    # Clean then copy.
    remove_all()
    shutil.copytree(src_gotcha, dst_gotcha)

    # Call DUNES with '--help' flag and test for the expected result.
    completed_process = subprocess.run([DUNES_EXE, "--help"], check=True, stdout=subprocess.PIPE)
    assert 'Could not load' in completed_process.stdout.decode()

    # Cleanup.
    remove_all()



if __name__ == "__main__":
    test_hello()
    test_fail()
    test_missing_main()
    test_gotcha()
