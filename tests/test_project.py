#!/usr/bin/env python3

"""Test DUNES Version

This script tests work with the a smart contract project keys:
  --create-cmake-app
  --create-bare-app
  --cmake-build
  --ctest
  --gdb
"""

import glob
import os
import shutil
import subprocess
import pytest

from common import DUNES_EXE, TEST_PATH, TEST_CONTAINER_NAME, TEST_IMAGE_NAME, stop_dunes_containers
from container import container


PROJECT_NAME = "test_app"
TEST_APP_DIR = os.path.join(TEST_PATH, PROJECT_NAME)
TEST_APP_BLD_DIR = os.path.join(TEST_APP_DIR, *["build", PROJECT_NAME])
TEST_APP_WASM = os.path.join(TEST_APP_BLD_DIR, PROJECT_NAME+".wasm")    # TEST_APP_BLD_DIR/test_app.wasm"


@pytest.mark.safe
def test_init():
    stop_dunes_containers()


def remove_existing():
    """ Remove an existing `./test_app` dir. """

    cntr = container(TEST_CONTAINER_NAME, TEST_IMAGE_NAME)
    cntr.stop()

    if os.path.exists(TEST_APP_DIR):
        print("Removing TEST_APP_DIR: ", TEST_APP_DIR)
        shutil.rmtree(TEST_APP_DIR)


@pytest.mark.safe
def test_create_cmake_app():
    """Test `--create-cmake-app` key."""

    remove_existing()

    # Expected files.
    filelist = [os.path.join(TEST_APP_DIR, 'src'),
                os.path.join(TEST_APP_DIR, *['src', PROJECT_NAME+'.cpp']),
                os.path.join(TEST_APP_DIR, *['src', 'CMakeLists.txt']),
                os.path.join(TEST_APP_DIR, 'include'),
                os.path.join(TEST_APP_DIR, *['include', PROJECT_NAME+'.hpp']),
                os.path.join(TEST_APP_DIR, 'ricardian'),
                os.path.join(TEST_APP_DIR, *['ricardian', PROJECT_NAME+'.contracts.md']),
                os.path.join(TEST_APP_DIR, 'build'),
                os.path.join(TEST_APP_DIR, 'CMakeLists.txt'),
                os.path.join(TEST_APP_DIR, 'README.txt')]

    # Create the test app.
    completed_process = subprocess.run([DUNES_EXE, '-C', TEST_CONTAINER_NAME, "--create-cmake-app", PROJECT_NAME, TEST_PATH], check=True)
    assert completed_process.returncode == 0
    assert os.path.isdir(TEST_APP_DIR) is True

    # Get a list of the files created.
    lst = glob.glob(TEST_APP_DIR + "/**", recursive=True)

    # Sort the lists and compare.
    filelist.sort()
    lst.sort()
    assert filelist == lst[1:]

    # Cleanup
    shutil.rmtree(TEST_APP_DIR)


@pytest.mark.safe
def test_create_bare_app():
    """Test `--create-bare-app` key."""

    remove_existing()

    # Expected file list.
    filelist = [os.path.join(TEST_APP_DIR, PROJECT_NAME+'.hpp'),
                os.path.join(TEST_APP_DIR, PROJECT_NAME+'.cpp'),
                os.path.join(TEST_APP_DIR, PROJECT_NAME+'.contracts.md'),
                os.path.join(TEST_APP_DIR, 'README.txt')]

    subprocess.run([DUNES_EXE, '-C', TEST_CONTAINER_NAME, "--create-bare-app", PROJECT_NAME, TEST_PATH], check=True)
    assert os.path.isdir(TEST_APP_DIR) is True

    # Actual file list.
    lst = glob.glob(TEST_APP_DIR + "/**", recursive=True)

    # Sort and compare expected and actual.
    filelist.sort()
    lst.sort()
    assert filelist == lst[1:]

    # Cleanup
    shutil.rmtree(TEST_APP_DIR)


@pytest.mark.safe
def test_cmake_and_ctest():
    """Test `--cmake` and `--ctest` key."""

    remove_existing()

    # Create the cmake app, test it exists.
    subprocess.run([DUNES_EXE, '-C', TEST_CONTAINER_NAME, "--create-cmake-app", PROJECT_NAME, TEST_PATH], check=True)
    assert os.path.isdir(TEST_APP_DIR) is True

    # Build the app, test that the expected output file is created.
    subprocess.run([DUNES_EXE, '-C', TEST_CONTAINER_NAME, "--cmake-build", TEST_APP_DIR], check=True)
    assert os.path.isfile(TEST_APP_WASM) is True

    # Test that CTest files are run.
    #    @TODO - This should be updated to create and test some PASSING tests.
    #    @TODO - This should be updated to create and test some FAILING tests.
    with subprocess.Popen(
            [DUNES_EXE, '-C', TEST_CONTAINER_NAME, "--debug", "--ctest", TEST_APP_DIR, "--", "--no-tests=ignore"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8") as proc:
        stdout, _ = proc.communicate()

        assert "No tests were found!!!" in stdout

    shutil.rmtree(TEST_APP_DIR)


@pytest.mark.safe
def test_gdb():
    """Test `--gdb` key."""

    # Simply ensure gdb is run.
    proc = subprocess.run([DUNES_EXE, '-C', TEST_CONTAINER_NAME, "--gdb", "/bin/sh"], capture_output=True, encoding="utf-8", check=True)
    assert "GNU gdb" in proc.stdout
