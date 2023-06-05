#!/usr/bin/env python3

"""Test DUNES Version

This script tests work with the crypto keys:
--create-key
--import-dev-key

"""
import subprocess
import pytest

from common import DUNES_EXE
from container import container


@pytest.mark.safe
def test_create_and_import_keys():
    """Test `--create-key` and `--import-dev-key` key."""

    # Ensure a container exists.
    cntr = container('dunes_container', 'dunes:latest')
    if not cntr.exists():
        assert cntr.create(), "Failed to create a container. You probably need to create and image with `bootstrap.py`."

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
    assert public_key is not None
    assert private_key is not None

    # Import the key.
    subprocess.run([DUNES_EXE, "--import-dev-key", private_key], check=True)
