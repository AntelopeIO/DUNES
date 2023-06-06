#!/usr/bin/env python3

"""Test of intergration of antler-proj to DUNES

This script tests following keys:
--create-project
--add-app
--add-lib
--add-dep
--remove-app
--remove-lib
--remove-dep
--update-app
--update-lib
--update-dep
--build-project
--clean-build-project

"""

import os
import shutil
import subprocess
import pytest

from common import DUNES_EXE, TEST_PATH


TEST_PROJECT_DIR = os.path.join(TEST_PATH, "antler_test_dir")


def remove_existing():
    """ Remove an existing `TEST_PROJECT_DIR` dir. """

    if os.path.exists(TEST_PROJECT_DIR):
        print("Removing a test directory if exists: ", TEST_PROJECT_DIR)
        shutil.rmtree(TEST_PROJECT_DIR)


@pytest.mark.skip(reason="Skipped until the release of antler-proj. "
                         "See details in https://github.com/AntelopeIO/DUNES/issues/134")
@pytest.mark.safe
def test_antler():

    remove_existing()

    subprocess.run([DUNES_EXE, "--create-project", "test_proj", TEST_PROJECT_DIR], check=True)

    # Add ------------

    subprocess.run([DUNES_EXE, "--add-app", TEST_PROJECT_DIR, "test_app", "c++",
                    "compiler_opts", "linker_opts"], check=True)
    res = subprocess.run([DUNES_EXE, "--debug", "--add-app", TEST_PROJECT_DIR, "test_app", "c++",
                          "compiler_opts", "linker_opts"], stdout=subprocess.PIPE, check=True)
    assert b'already exists in project' in res.stdout

    subprocess.run([DUNES_EXE, "--add-lib", TEST_PROJECT_DIR, "test_lib", "c++",
                    "compiler_opts", "linker_opts"], check=True)
    res = subprocess.run([DUNES_EXE, "--debug", "--add-lib", TEST_PROJECT_DIR, "test_lib", "c++",
                          "compiler_opts", "linker_opts"], stdout=subprocess.PIPE, check=True)
    assert b'already exists in project' in res.stdout

    # this test is commented because adding of dependencies doesn't work
    # subprocess.run([DUNES_EXE, "--add-dep", TEST_PROJECT_DIR, "test_app",  "test_dep",
    #                 "larryk85/sample_contract", "0.0.1", "hash"], check=True)
    # res = subprocess.run([DUNES_EXE, "--debug", "--add-dep", TEST_PROJECT_DIR, "test_app",  "test_dep",
    #                       "larryk85/sample_contract", "0.0.1", "hash"],
    #                      stdout=subprocess.PIPE)
    # assert b'already exists for' in res.stdout


# Remove ------------

    subprocess.run([DUNES_EXE, "--remove-app", TEST_PROJECT_DIR, "test_app"], check=True)
    res = subprocess.run([DUNES_EXE, "--debug", "--add-app", TEST_PROJECT_DIR, "test_app", "c++",
                          "compiler_opts", "linker_opts"], stdout=subprocess.PIPE, check=True)
    assert b'already exists in project' not in res.stdout

    subprocess.run([DUNES_EXE, "--remove-lib", TEST_PROJECT_DIR, "test_lib"], check=True)
    res = subprocess.run([DUNES_EXE, "--debug", "--add-lib", TEST_PROJECT_DIR, "test_lib", "c++",
                          "compiler_opts", "linker_opts"], stdout=subprocess.PIPE, check=True)
    assert b'already exists in project' not in res.stdout

    remove_existing()
