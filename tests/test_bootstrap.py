#!/usr/bin/env python3

"""Test DUNES bootstrap

These options are tested:
  --create-key
  --import-dev-key
  --bootstrap-system-full
  --get-table
"""

import subprocess
import pytest

from common import DUNES_EXE

# Globals
NODE_NAME = "my_node"
ACCT_NAME = "myaccount"
ACCT_NAME2 = "myaccount2"


@pytest.mark.destructive
def test_booststrap():

    # Remove any existing containers.
    subprocess.run([DUNES_EXE, "--destroy-container"], check=True)

    # Start the new node.
    subprocess.run([DUNES_EXE, "--start", NODE_NAME], check=True)

    # Create an account.
    subprocess.run([DUNES_EXE, "--create-account", ACCT_NAME], check=True)

    account_results = subprocess.run([DUNES_EXE, "--", "cleos", "get", "account", ACCT_NAME], check=True, stdout=subprocess.PIPE)
    assert b'created:' in account_results.stdout

    # Create a key. Get it to a var as well.
    public_key = None
    private_key = None
    stdout_result = subprocess.run([DUNES_EXE, "--create-key"], check=True, stdout=subprocess.PIPE)
    result_list = stdout_result.stdout.decode().split("\n")
    for entry in result_list:
        # ignore empty entries.
        if len(entry) == 0:
            continue
        items = entry.split(': ')
        if len(items) == 2:
            if items[0] == "Private key":
                private_key = items[1]
            elif items[0] == "Public key":
                public_key = items[1]
    assert private_key is not None

    # Import the key.
    subprocess.run([DUNES_EXE, "--import-dev-key", private_key], check=True)

    # Bootstrap the system.
    subprocess.run([DUNES_EXE, "--bootstrap-system"], check=True)

    # Create a second account
    subprocess.run([DUNES_EXE, "--create-account", ACCT_NAME2], check=True)

    # Creation of second account should now be successful
    second_account_results = subprocess.run([DUNES_EXE, "--", "cleos", "get", "account", ACCT_NAME2],
                                            check=True, stdout=subprocess.PIPE)
    assert b'created:' in second_account_results.stdout

    # Verify that "Create New Account" has been deployed
    results = subprocess.run([DUNES_EXE, "--", "cleos", "get", "abi", "eosio"],
                             check=True, stdout=subprocess.PIPE)
    assert b'Create New Account' in results.stdout
