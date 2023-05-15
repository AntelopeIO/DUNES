#!/usr/bin/env python3

"""Test DUNE Plugin

This script tests that after copying plugin to src/plugin DUNE detects it and run properly.
"""

import os
import shutil
import subprocess

from common import DUNES_EXE

current_script_path = os.path.abspath(__file__)
current_script_dir = os.path.dirname(current_script_path)

src_dir = current_script_dir + '/../plugin_example/dune_hello'
dst_dir = current_script_dir + '/../src/plugin/dune_hello'

def prepare_plugin():
    remove_plugin()
    shutil.copytree(src_dir, dst_dir)

def remove_plugin():
    shutil.rmtree(dst_dir, ignore_errors=True)

def test_plugin_help():
    prepare_plugin()

    expect_list = \
        [
            b'--hello',
        ]

    # Call DUNE.
    completed_process = subprocess.run([DUNES_EXE, "--help"], check=True, stdout=subprocess.PIPE)

    # Test for expected values in the captured output.
    for expect in expect_list:
        assert expect in completed_process.stdout

    remove_plugin()


def test_plugin_execution():
    prepare_plugin()

    expect_list = \
        [
            b'Hello from DUNE',
        ]

    # Call DUNE.
    completed_process = subprocess.run([DUNES_EXE, "--hello"], check=True, stdout=subprocess.PIPE)

    # Test for expected values in the captured output.
    for expect in expect_list:
        assert expect in completed_process.stdout

    remove_plugin()
    