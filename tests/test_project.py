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

from common import DUNE_EXE


TEST_APP_DIR = "./test_app"


def remove_existing():
    """ Remove an existing `./test_app` dir. """

    if os.path.exists(TEST_APP_DIR):
        print("Removing TEST_APP_DIR: ", TEST_APP_DIR)
        shutil.rmtree(TEST_APP_DIR)


def test_create_cmake_app():
    """Test `--create-cmake-app` key."""

    remove_existing()

    # Expected files.
    filelist = ['./test_app/',
                './test_app/src',
                './test_app/src/test_app.cpp',
                './test_app/src/CMakeLists.txt',
                './test_app/include',
                './test_app/include/test_app.hpp',
                './test_app/ricardian',
                './test_app/ricardian/test_app.contracts.md',
                './test_app/build',
                './test_app/CMakeLists.txt',
                './test_app/README.txt']

    # Create the test app.
    subprocess.run([DUNE_EXE, "--create-cmake-app", "test_app", "./"], check=True)
    assert os.path.isdir("./test_app") is True

    # Get a list of the files created.
    lst = glob.glob("./test_app/**", recursive=True)

    # Sort the lists and compare.
    filelist.sort()
    lst.sort()
    assert filelist == lst

    # Cleanup
    shutil.rmtree("./test_app")


def test_create_bare_app():
    """Test `--create-bare-app` key."""

    remove_existing()

    # Expected file list.
    filelist = ['./test_app/',
                './test_app/test_app.hpp',
                './test_app/test_app.cpp',
                './test_app/test_app.contracts.md',
                './test_app/README.txt']


    subprocess.run([DUNE_EXE, "--create-bare-app", "test_app", "./"], check=True)
    assert os.path.isdir("./test_app") is True

    # Actual file list.
    lst = glob.glob("./test_app/**", recursive=True)

    # Sort and compare expected and actual.
    filelist.sort()
    lst.sort()
    assert filelist == lst

    # Cleanup
    shutil.rmtree("./test_app")



def test_cmake_and_ctest():
    """Test `--cmake` and `--ctest` key."""

    remove_existing()

    # Create the cmake app, test it exists.
    subprocess.run([DUNE_EXE, "--create-cmake-app", "test_app", "./"], check=True)
    assert os.path.isdir("./test_app") is True

    # Build the app, test that the expected output file is created.
    subprocess.run([DUNE_EXE, "--cmake-build", "./test_app"], check=True)
    assert os.path.isfile("./test_app/build/test_app/test_app.wasm") is True

    # Test that CTest files are run.
    #    @TODO - This should be updated to create and test some PASSING tests.
    #    @TODO - This should be updated to create and test some FAILING tests.
    with subprocess.Popen(
            [DUNE_EXE, "--debug", "--ctest", "./test_app", "--", "--no-tests=ignore"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8") as proc:
        stdout, stderr = proc.communicate()

        assert "No tests were found!!!" in stderr


    shutil.rmtree("./test_app")


def test_gdb():
    """Test `--gdb` key."""

    # Simply ensure gdb is run.
    proc = subprocess.run([DUNE_EXE, "--gdb", "/bin/sh"], capture_output=True, encoding="utf-8", check=True)
    assert "GNU gdb" in proc.stdout
