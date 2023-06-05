#!/usr/bin/env python3

"""Ensure Container Image Version

This script tests that the container image being tested is correct.
"""

import sys
import os
import subprocess
import pytest

from common import TEST_PATH, DUNES_EXE, DUNES_ROOT


def get_short_hash():
    """Try to get the short hash for this repo."""

    # Find the short hash or warn and return empty string.
    try:
        return subprocess.check_output(['git', '-C', TEST_PATH, 'rev-parse', '--short', 'HEAD'], stderr=None, encoding='utf-8').strip()
    # pylint: disable=bare-except
    except:
        print( "Failed to determine git short hash." )
    return ''


def get_dunes_version():
    """Try to get the version of this DUNES tool."""

    # Find the version or warn and return empty string.
    try:
        return subprocess.check_output([DUNES_EXE, '--version-short'], stderr=None, encoding='utf-8').strip()
    # pylint: disable=bare-except
    except:
        print( "Failed to determine DUNES version." )
    return ''


def get_image_id(tag):
    """Try to get the ID of a an image given its tag."""

    image_name = 'dunes:' + tag
    try:
        return subprocess.check_output(['docker', 'image', 'list', '-q', image_name], stderr=None, encoding='utf-8').strip()
    # pylint: disable=bare-except
    except:
        print( f"Could not get results from docker for image: {image_name}." )
    return ''


def remove_images(repo_name):
    """
    Remove any existing repo images.
    WARNING: This is destructive.
    """

    # Remove {repo_name}:* images.
    images = subprocess.check_output(['docker', 'images', '-q', repo_name], stderr=None, encoding='utf-8').strip().split('\n')
    for myimg in images:
        #   pylint: disable=subprocess-run-check
        subprocess.run(['docker', 'image', 'rm', myimg, '--force'], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL, check=False)


def remove_tagged_image(tag):
    """
    Remove any existing tagged images.
    WARNING: This is destructive.
    """

    #   pylint: disable=subprocess-run-check
    subprocess.run(['docker', 'image', 'rm', tag, '--force'], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL, check=False)


def clean_destructive():
    """
    Remove any existing dunes_container and/or dunes images.
    WARNING: This is destructive.
    """

    # Remove an existing container, then images.
    # Send output to subprocess.DEVNULL since we EXPECT docker might tell us containers and images don't exist.
    #   pylint: disable=subprocess-run-check, line-too-long
    subprocess.run(['docker', 'container', 'rm', 'dunes_container', '--force'], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL, check=False)
    # Remove dunes:* images.
    remove_images('dunes')
    # Remove ghcr.io/antelopeio/dunes:* images.
    remove_images('ghcr.io/antelopeio/dunes')


def image_exists(tag):
    """Test to see if a given image exists."""
    # Get the list of images.
    uid = subprocess.check_output(['docker', 'images', '-q', tag], stderr=None, encoding='utf-8')
    if uid == '':
        return False
    return True


@pytest.mark.destructive
def test_release_versions_destructive():
    """
    Ensure bootsrap can be created with --release flag.
    This test will also ensure the follow on test (test_ensure_conatiner_image) has a latests image.
    This test normally needs to be run BEFORE all other tests to ensure the containers exist.
    """

    clean_destructive()

    # Find the current version and short hash of DUNES.
    dunes_version = get_dunes_version()
    short_hash = get_short_hash()

    critical_images = [ f'dunes:{dunes_version}',
                        f'dunes:{short_hash}',
                        'ghcr.io/antelopeio/dunes:latest',
                        f'ghcr.io/antelopeio/dunes:{dunes_version}',
                        ]

    # Ensure the critical images are absent.
    for myimg in critical_images:
        assert not image_exists(myimg)

    # Execute the bootstrap function.
    bootstrap_command = [sys.executable, os.path.join(DUNES_ROOT, "bootstrap.py"), '--release']
    subprocess.run(bootstrap_command, check=True)

    # Ensure the critical images are present.
    for myimg in critical_images:
        assert image_exists(myimg)

    # Remove the ghcr images - they are unnecessary.
    remove_tagged_image('ghcr.io/antelopeio/dunes:latest')
    remove_tagged_image(f'ghcr.io/antelopeio/dunes:{dunes_version}')


@pytest.mark.destructive
def test_ensure_conatiner_image():
    """Ensure container version is available and correct."""

    # Try to get the short hash.
    short_hash = get_short_hash()

    # Determine the tag: use short hash if we have it; otherwise, use version.
    image_tag = ''
    if short_hash != '':
        image_tag = short_hash
    else:
        image_tag = get_dunes_version()
        # In the case that we have neither short hash nor version, we will fail assertion here:
        assert image_tag != '', "\n Could not determine what tag to use with either git or DUNES."
        print( "WARNING: Could not determine git short hash, reverting to DUNES version: ", image_tag )

    # Ensure failure text includes the source of the tag: short hash or version.
    determination_string = ''
    source_string = ''
    if short_hash != '':
        determination_string = f"We determined the short hash for this repo is {short_hash}."
        source_string = 'short hash'
    else:
        determination_string =f"Unable to determine the short hash for this repo - fell back to DUNES version: {image_tag}."
        source_string = 'version'

    # Search for the ID of the image and ensure it exists.
    image_id = get_image_id(image_tag)

    assert image_id != '', \
        f"\n {determination_string}" \
        f"\n Given the command 'docker image list -q dunes:{image_tag}', we expected a valid ID, but got an empty string." \
         "\n It's possible 'bootstrap.py' needs to be run to generate the correct image for these tests." \
         "\n If you are certain your version of the image is up to date, you can correct this by tagging:" \
        f"\n     docker tag dunes dunes:{image_tag}"

    # Search for the ID of the latest image and ensure it matches image_id.
    latest_id = get_image_id('latest')

    assert image_id == latest_id, \
        f"\n {source_string} tag: \t{image_tag} \t id: {image_id}" \
        f"\n location tag: \t{image_tag} \t id: {latest_id}"


if __name__ == "__main__":
    test_release_versions_destructive()
    test_ensure_conatiner_image()
