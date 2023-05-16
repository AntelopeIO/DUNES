#!/usr/bin/env python3

"""Ensure Container Image Version

This script tests that the container image being tested is correct.
"""


import subprocess

from common import TEST_PATH, DUNE_EXE


def get_short_hash():
    """Try to get the short hash for this repo."""

    # Find the short hash or warn and return empty string.
    try:
        return subprocess.check_output(['git', '-C', TEST_PATH, 'rev-parse', '--short', 'HEAD'], stderr=None, encoding='utf-8').strip()
    except:
        print( "Failed to determine git short hash." )
    return ''


def get_dune_version():
    """Try to get the version of this DUNES tool."""

    # Find the version or warn and return empty string.
    try:
        return subprocess.check_output([DUNE_EXE, '--version-short'], stderr=None, encoding='utf-8').strip()
    except:
        print( "Failed to determine DUNE version." )
    return ''


def get_image_id(tag):
    """Try to get the ID of a an image given its tag."""

    image_name = 'dune:' + tag
    try:
        return subprocess.check_output(['docker', 'image', 'list', '-q', image_name], stderr=None, encoding='utf-8').strip()
    except:
        print( f"Could not get results from docker for image: {image_name}." )
    return ''


def test_ensure_conatiner_image():
    """Ensure container version is available and correct."""

    # Try to get the short hash.
    short_hash = #get_short_hash()

    # Determine the tag: use short hash if we have it; otherwise, use version.
    image_tag = ''
    if short_hash != '':
        image_tag = short_hash
    else:
        image_tag = get_dune_version()
        # In the case that we have neither short hash nor version, we will fail assertion here:
        assert image_tag != '', \
            f"\n Could not determine what tag to use with either git or DUNE."
        print( "WARNING: Could not determine git short hash, reverting to DUNE version: ", image_tag )

    # Ensure failure text includes the source of the tag: short hash or version.
    determination_string = ''
    source_string = ''
    if short_hash != '':
        determination_string = f"We determined the short hash for this repo is {short_hash}."
        source_string = 'short hash'
    else:
        determination_string =f"Unable to determine the short hash for this repo - fell back to DUNE version: {image_tag}."
        source_string = 'version'

    # Search for the ID of the image and ensure it exists.
    image_id = get_image_id(image_tag)

    assert image_id != '', \
        f"\n {determination_string}" \
        f"\n Given the command 'docker image list -q dune:{image_tag}', we expected a valid ID, but got an empty string." \
        "\n It's possible 'bootstrap.sh' needs to be run to generate the correct image for these tests."


    # Search for the ID of the latest image and ensure it matches image_id.
    latest_id = get_image_id('latest')

    assert image_id == latest_id, \
        f"\n {source_string} tag: \t{image_tag} \t id: {image_id}" \
        f"\n location tag: \t{image_tag} \t id: {latest_id}"



if __name__ == "__main__":
    test_ensure_conatiner_image()
