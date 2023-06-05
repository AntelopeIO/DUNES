# conftest.py

import pytest


def pytest_addoption(parser):
    """Add these options to pytest itself."""

    # Add these flags to pytest itself.
    parser.addoption("--run-slow", action="store_true", default=False, help="run slow tests")
    parser.addoption("--run-destructive", action="store_true", default=False, help="run destructive tests")
    parser.addoption("--run-all", action="store_true", default=False, help="run all tests including slow and destructive tests")


def pytest_configure(config):
    """Add these to the config file."""

    # Warn about markers that aren't known.
    config.addinivalue_line("addopts", "--strict-markers", )

    # The list of known markers.
    config.addinivalue_line("markers", "slow: mark test as slow running")
    config.addinivalue_line("markers", "destructive: mark test as destructive to existing data including containers and images")
    config.addinivalue_line("markers", "safe: mark test as non-destructive")


def pytest_runtest_setup(item):
    """Enforce that a test must be marked either 'safe' or 'destructive'."""

    actual_marks = []
    has_required = False
    for mark in item.iter_markers():
        actual_marks.append(mark.name)
        if mark.name in ['safe','destructive']:
            has_required = True

    assert has_required, f"'{item.name}' has these markers: {actual_marks}, but one of 'safe' or 'destructive' is required."


def pytest_collection_modifyitems(config, items):
    """This test is run to make sure markers are skipped."""

    # No need to add skip to anything if the user says to run all!
    if config.getoption("--run-all"):
        return

    # If a test is marked with any of these it should be skipped by default.
    skip_markers = ['destructive', 'slow']

    # Remove any markers that the user wants to enable via a --run-<marker> flag.
    temp_markers = skip_markers
    for marker in temp_markers:
        # Calculate the marker's run flag and test to see if it's NOT set.
        flag = f'--run-{marker}'
        if config.getoption(flag):
            skip_markers.remove(marker)

    # If there's nothing to skip, we return.
    if not skip_markers:
        return

    # Iterate over all the items and see if any need to be skipped.
    for item in items:

        # Figure out which flags the user needs to add to ensure a test runs.
        required_flags = []
        for marker in skip_markers:
            if marker in item.keywords:
                required_flags.append(f'--run-{marker}')

        # Add the skip mark and reason to the item if needed.
        if required_flags:
            sep = ' and '
            #skip_mark = pytest.mark.skip(reason=f"require {sep.join(required_flags)} OR --run-all option to run")
            skip_mark = pytest.mark.skip(reason=f"require {sep.join(required_flags)} to run")
            item.add_marker(skip_mark)
