#!/usr/bin/env python3

"""Test DUNES Version

This script tests export and import of the wallet
"""

import os
import shutil
import subprocess

from container import container
from common import DUNES_EXE


def tar_dir(file_name, directory):
    subprocess.run(['tar', 'cvzf', file_name + '.tgz', directory], check=True)


def untar(file_name):
    subprocess.run(['tar', 'xvzf', file_name], check=True)


def test_export():
    """Test `--export-wallet` key."""

    subprocess.run([DUNES_EXE, "--export-wallet"], check=True)

    assert os.path.exists("wallet.tgz") is True


def test_import():
    """Test `--import-wallet` key."""

    cntr = container('dunes_container', 'dunes:latest')

    cntr.rm_file("/app/wallet.tgz")

    assert os.path.exists("wallet.tgz") is True

    untar("wallet.tgz")

    # Platform dependent locale encoding is acceptable here.
    #   pylint: disable=unspecified-encoding
    with open("_wallet/eosio-wallet/import_test_file", "w") as flag_file:
        flag_file.write("this is a flag file for testing purposes")

    tar_dir("wallet", "_wallet")

    # Use wallet.tgz created by successfully finished test of export
    subprocess.run([DUNES_EXE, "--debug", "--import-wallet", "./wallet.tgz"], check=True)

    os.remove("wallet.tgz")
    shutil.rmtree("_wallet")

    assert cntr.file_exists("/root/eosio-wallet/import_test_file") is True

    cntr.rm_file("/root/eosio-wallet/import_test_file")
