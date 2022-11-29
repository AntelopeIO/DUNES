#!/usr/bin/env python3

"""Test DUNE Functions.

This script tests work with the smart contract related keys:
  --deploy
  --send-action
"""

import os
import shutil
import subprocess

from common import DUNE_EXE,TEST_PATH

# Globals
NODE_NAME = "my_node"
ACCT_NAME = "myaccount"

PROJECT_NAME = "test_app"
TEST_APP_DIR = TEST_PATH + "/" + PROJECT_NAME
TEST_APP_BLD_DIR = TEST_APP_DIR + "/build/" + PROJECT_NAME
TEST_APP_WASM = TEST_APP_BLD_DIR + "/" + PROJECT_NAME + ".wasm"    # TEST_APP_BLD_DIR + "/test_app.wasm"


def test_deploy():
    """Test `--deploy` key."""

    # Remove any existing containers and old build directories.
    subprocess.run([DUNE_EXE,"--destroy-container"], check=True)
    if os.path.exists(TEST_APP_DIR):
        print("Removing TEST_APP_DIR: ", TEST_APP_DIR)
        shutil.rmtree(TEST_APP_DIR)

    # Create a new node and an account.
    subprocess.run([DUNE_EXE, "--start", NODE_NAME], check=True)
    subprocess.run([DUNE_EXE, "--create-account", ACCT_NAME], check=True)

    # Create and build a test app.
    subprocess.run([DUNE_EXE, "--create-cmake-app", PROJECT_NAME, TEST_PATH], check=True)
    subprocess.run([DUNE_EXE, "--cmake-build", TEST_APP_DIR], check=True)
    assert os.path.isfile(TEST_APP_WASM) is True

    subprocess.run([DUNE_EXE, "--deploy", TEST_APP_BLD_DIR, ACCT_NAME], check=True)

    # Send the action and search for a response in the result.
    #   ./dune --debug --send-action myaccount hi ["test"] eosio@active
    results = subprocess.run([DUNE_EXE, "--send-action", ACCT_NAME, "hi", '["test"]', "eosio@active"], check=True, stdout=subprocess.PIPE)
    assert b'>> Name : test' in results.stdout

    # Clean up after tests.
    shutil.rmtree(TEST_APP_DIR)
