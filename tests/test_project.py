#!/usr/bin/env python3

"""Test DUNE Version

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

from common import DUNE_EXE,TEST_PATH
from container import container


PROJECT_NAME = "test_app"
TEST_APP_DIR = TEST_PATH + "/" + PROJECT_NAME
TEST_APP_BLD_DIR = TEST_APP_DIR + "/build/" + PROJECT_NAME
TEST_APP_WASM = TEST_APP_BLD_DIR + "/" + PROJECT_NAME + ".wasm"    # TEST_APP_BLD_DIR + "/test_app.wasm"


def remove_existing():
    """ Remove an existing `./test_app` dir. """

    cntr = container('dune_container', 'dune:latest')
    cntr.stop()

    if os.path.exists(TEST_APP_DIR):
        print("Removing TEST_APP_DIR: ", TEST_APP_DIR)
        shutil.rmtree(TEST_APP_DIR)


def test_create_cmake_app():
    """Test `--create-cmake-app` key."""

    remove_existing()

    # Expected files.
    filelist = [TEST_APP_DIR + '/',
                TEST_APP_DIR + '/src',
                TEST_APP_DIR + '/src/' + PROJECT_NAME + '.cpp',
                TEST_APP_DIR + '/src/CMakeLists.txt',
                TEST_APP_DIR + '/include',
                TEST_APP_DIR + '/include/' + PROJECT_NAME + '.hpp',
                TEST_APP_DIR + '/ricardian',
                TEST_APP_DIR + '/ricardian/' + PROJECT_NAME + '.contracts.md',
                TEST_APP_DIR + '/build',
                TEST_APP_DIR + '/CMakeLists.txt',
                TEST_APP_DIR + '/README.txt']

    # Create the test app.
    completed_process = subprocess.run([DUNE_EXE, "--create-cmake-app", PROJECT_NAME, TEST_PATH], check=True)
    assert completed_process.returncode == 0
    assert os.path.isdir(TEST_APP_DIR) is True

    # Get a list of the files created.
    lst = glob.glob(TEST_APP_DIR + "/**", recursive=True)

    # Sort the lists and compare.
    filelist.sort()
    lst.sort()
    assert filelist == lst

    # Cleanup
    shutil.rmtree(TEST_APP_DIR)


def test_create_bare_app():
    """Test `--create-bare-app` key."""

    remove_existing()

    # Expected file list.
    filelist = [TEST_APP_DIR + '/',
                TEST_APP_DIR + '/' + PROJECT_NAME + '.hpp',
                TEST_APP_DIR + '/' + PROJECT_NAME + '.cpp',
                TEST_APP_DIR + '/' + PROJECT_NAME + '.contracts.md',
                TEST_APP_DIR + '/README.txt']


    subprocess.run([DUNE_EXE, "--create-bare-app", PROJECT_NAME, TEST_PATH], check=True)
    assert os.path.isdir(TEST_APP_DIR) is True

    # Actual file list.
    lst = glob.glob(TEST_APP_DIR + "/**", recursive=True)

    # Sort and compare expected and actual.
    filelist.sort()
    lst.sort()
    assert filelist == lst

    # Cleanup
    shutil.rmtree(TEST_APP_DIR)



def test_cmake_and_ctest():
    """Test `--cmake` and `--ctest` key."""

    remove_existing()

    # Create the cmake app, test it exists.
    subprocess.run([DUNE_EXE, "--create-cmake-app", PROJECT_NAME, TEST_PATH], check=True)
    assert os.path.isdir(TEST_APP_DIR) is True

    # Build the app, test that the expected output file is created.
    subprocess.run([DUNE_EXE, "--cmake-build", TEST_APP_DIR], check=True)
    assert os.path.isfile(TEST_APP_WASM) is True

    # Test that CTest files are run.
    #    @TODO - This should be updated to create and test some PASSING tests.
    #    @TODO - This should be updated to create and test some FAILING tests.
    with subprocess.Popen(
            [DUNE_EXE, "--debug", "--ctest", TEST_APP_DIR, "--", "--no-tests=ignore"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8") as proc:
        stdout, _ = proc.communicate()

        assert "No tests were found!!!" in stdout

    shutil.rmtree(TEST_APP_DIR)


def test_gdb():
    """Test `--gdb` key."""

    # Simply ensure gdb is run.
    proc = subprocess.run([DUNE_EXE, "--gdb", "/bin/sh"], capture_output=True, encoding="utf-8", check=True)
    assert "GNU gdb" in proc.stdout
