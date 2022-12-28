#!/usr/bin/env python3

"""Test DUNE Version_

This script tests that the compiled binary produce expected output
in response to `--version` option.
"""

import subprocess
import pytest

from common import TEST_PATH

@pytest.mark.skip(reason="Missing option: --bootstrap-system,Missing option: --get-table,Missing option: --activate-feature")
def test_all_options_tested():
    """Test that all the options from the output of `--help` are in the various test files."""

    script=TEST_PATH+"/show_untested_options.sh"

    subprocess.run(script, check=True)
