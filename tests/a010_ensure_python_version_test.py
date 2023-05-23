#!/usr/bin/env python3

"""Ensure Python is the correct version for tests"""


import platform


def test_python_version():
    """Ensure python version is acceptable."""

    minimum = (3,7,0)
    version = (0,0,0)

    try:
        vstr = platform.python_version_tuple()
        version = (int(vstr[0]), int(vstr[1]), int(vstr[2]))
    # pylint: disable=bare-except
    except:
        assert False, "Failed to determine Python version, expect minimum {minimum}."

    assert version >= minimum, f'Minimum acceptable Python version is {minimum}, found version {version}.'


if __name__ == "__main__":
    test_python_version()
