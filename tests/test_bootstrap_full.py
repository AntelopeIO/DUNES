#!/usr/bin/env python3

"""Test DUNES bootstrap

These options are tested:
  --create-key
  --import-dev-key
  --bootstrap-system-full
  --get-table
"""

import subprocess

from common import DUNES_EXE

# Globals
NODE_NAME = "my_node"
ACCT_NAME = "myaccount"
ACCT_NAME2 = "myaccount2"


def test_booststrap():

    # Remove any existing containers.
    subprocess.run([DUNES_EXE, "--destroy-container"], check=True)

    # Start the new node.
    subprocess.run([DUNES_EXE, "--start", NODE_NAME], check=True)

    # Create an account.
    subprocess.run([DUNES_EXE, "--create-account", ACCT_NAME], check=True)

    account_results = subprocess.run([DUNES_EXE, "--", "cleos", "get", "account", ACCT_NAME],
                                     check=True, stdout=subprocess.PIPE)
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
    subprocess.run([DUNES_EXE, "--bootstrap-system-full"], check=True)

    # Create a second account should fail because of not enough RAM
    subprocess.run([DUNES_EXE, "--create-account", ACCT_NAME2], check=False)

    second_account_results = subprocess.run([DUNES_EXE, "--", "cleos", "get", "account", ACCT_NAME2],
                                            check=False, stdout=subprocess.PIPE)
    assert b'created:' not in second_account_results.stdout

    # Create an example account with RAM
    subprocess.run([DUNES_EXE, "--system-newaccount", ACCT_NAME2, "eosio",
                    "EOS8C5BLCX2LrmcRLHMC8bN5mML4aFSHrZvyijzfLy48tiije6nTt",
                    "5KNitA34Usr2EVLQKtFrwAJVhyB2F3U7fDHEuP2ee2zZ16w7PeB",
                    "--", "--stake-net", "1.0000 SYS", "--stake-cpu", "1.0000 SYS",
                    "--buy-ram-bytes", "3000"], check=True)

    # Creation of second account should now be successful
    second_account_results = subprocess.run([DUNES_EXE, "--", "cleos", "get", "account", ACCT_NAME2],
                                            check=True, stdout=subprocess.PIPE)
    assert b'created:' in second_account_results.stdout

    results = subprocess.run([DUNES_EXE, "--get-table", "eosio.token", "eosio", "accounts"],
                             check=True, stdout=subprocess.PIPE)
    assert b'"rows"' in results.stdout
