#!/usr/bin/env python3

"""Test DUNES List Features

This script tests that the compiled binary produce expected output in
response to the `--list-features` option.
"""


import subprocess
import pytest

from common import DUNES_EXE, stop_dunes_containers


@pytest.mark.safe
def test_init():
    stop_dunes_containers()


@pytest.mark.safe
def test_list_features():
    """Test that the output of `dunes --list-features` is as expected."""

    # List of expected output lines from `dunes --list-features`.
    expect_list = \
	["GET_CODE_HASH",
        "CRYPTO_PRIMITIVES",
        "GET_BLOCK_NUM",
        "ACTION_RETURN_VALUE",
        "CONFIGURABLE_WASM_LIMITS2",
        "BLOCKCHAIN_PARAMETERS",
        "GET_SENDER",
        "FORWARD_SETCODE",
        "ONLY_BILL_FIRST_AUTHORIZER",
        "RESTRICT_ACTION_TO_SELF",
        "DISALLOW_EMPTY_PRODUCER_SCHEDULE",
        "FIX_LINKAUTH_RESTRICTION",
        "REPLACE_DEFERRED",
        "NO_DUPLICATE_DEFERRED_ID",
        "ONLY_LINK_TO_EXISTING_PERMISSION",
        "RAM_RESTRICTIONS",
        "WEBAUTHN_KEY",
        "WTMSIG_BLOCK_SIGNATURES"]

    # Convert the list to a useful comparison value.
    expect = ''
    for temp in expect_list:
        expect = expect + temp + '\n'

    subprocess.run([DUNES_EXE, "--start-container"], check=True, stdout=subprocess.PIPE)
    # Call the tool, check return code, check expected value.
    completed_process = subprocess.run([DUNES_EXE, "--list-features"], check=True, stdout=subprocess.PIPE)
    assert completed_process.stdout.decode().replace('\r', '') == expect
