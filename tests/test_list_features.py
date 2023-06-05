#!/usr/bin/env python3

"""Test DUNES List Features

This script tests that the compiled binary produce expected output in
response to the `--list-features` option.
"""


import subprocess
import pytest

from common import DUNES_EXE


@pytest.mark.safe
def test_list_features():
    """Test that the output of `dunes --list-features` is as expected."""

    # List of expected output lines from `dunes --list-features`.
    expect_list = \
	[b"GET_CODE_HASH",
        b"CRYPTO_PRIMITIVES",
        b"GET_BLOCK_NUM",
        b"ACTION_RETURN_VALUE",
        b"CONFIGURABLE_WASM_LIMITS2",
        b"BLOCKCHAIN_PARAMETERS",
        b"GET_SENDER",
        b"FORWARD_SETCODE",
        b"ONLY_BILL_FIRST_AUTHORIZER",
        b"RESTRICT_ACTION_TO_SELF",
        b"DISALLOW_EMPTY_PRODUCER_SCHEDULE",
        b"FIX_LINKAUTH_RESTRICTION",
        b"REPLACE_DEFERRED",
        b"NO_DUPLICATE_DEFERRED_ID",
        b"ONLY_LINK_TO_EXISTING_PERMISSION",
        b"RAM_RESTRICTIONS",
        b"WEBAUTHN_KEY",
        b"WTMSIG_BLOCK_SIGNATURES"]

    # Convert the list to a useful comparison value.
    expect = b''
    for temp in expect_list:
        expect = expect + temp + b'\n'

    # Call the tool, check return code, check expected value.
    completed_process = subprocess.run([DUNES_EXE, "--list-features"],
                                       check=True, stdout=subprocess.PIPE)
    assert completed_process.stdout == expect
