#!/usr/bin/env python3

"""Test DUNES Version_

This script tests that the compiled binary produce expected output
in response to `--version` option.
"""

import subprocess
import pytest

from common import TEST_PATH


@pytest.mark.xfail
@pytest.mark.safe
def test_all_options_tested():
    """Test that all the options from the output of `--help` are in the various test files."""

    # pylint: disable=fixme
    # TODO: convert show_untested_options.sh to python that runs here.
    script = TEST_PATH+"/show_untested_options.sh"

    subprocess.run(script, check=True)
