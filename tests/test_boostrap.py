#!/usr/bin/env python3

"""Test DUNE bootstrap

These options are tested:
  --create-key
  --import-dev-key
  --bootstrap-system-full
  --get-table
"""

import subprocess

from common import DUNE_EXE

# Globals
NODE_NAME = "my_node"
ACCT_NAME = "myaccount"


def test_booststrap():

    # Remove any existing containers.
    subprocess.run([DUNE_EXE, "--destroy-container"], check=True)

    # Start the new node.
    subprocess.run([DUNE_EXE, "--start",NODE_NAME], check=True)

    # Create an account.
    subprocess.run([DUNE_EXE, "--create-account",ACCT_NAME], check=True)

    # Create a key. Get it to a var as well.
    public_key = None
    private_key = None
    stdout_result = subprocess.run([DUNE_EXE,"--create-key"], check=True, stdout=subprocess.PIPE)
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
    subprocess.run([DUNE_EXE, "--import-dev-key",private_key], check=True)

    # Bootstrap the system.
    subprocess.run([DUNE_EXE, "--bootstrap-system-full"], check=True)

    results = subprocess.run([DUNE_EXE, "--get-table", "eosio.token", "eosio", "accounts"], check=True, stdout=subprocess.PIPE)
    assert b'"rows"' in results.stdout
